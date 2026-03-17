---
applyTo: "**/*.go,**/go.mod,**/go.sum"
---

# Go Conventions

> Philosophy: **simplicity, readability, explicitness**. Go code should be boring in the best sense — straightforward, predictable, easy to review. Embrace the standard library; reach for dependencies only when justified.
>
> **Prerequisites**: Go ≥ 1.22, golangci-lint, goimports

---

## Naming conventions

### Packages

- Short, lowercase, single-word names: `user`, `order`, `auth`
- No underscores, no camelCase: `httputil` not `httpUtil` or `http_util`
- Package name should not repeat the parent directory: `net/http` not `net/httppackage`
- Avoid generic names like `util`, `common`, `helpers` — be specific

### Functions & methods

- Exported: `PascalCase` — `CreateUser`, `ParseToken`
- Unexported: `camelCase` — `validateInput`, `buildQuery`
- Constructors: `New<Type>` — `NewUserService`, `NewRouter`
- Getters: no `Get` prefix — `user.Name()` not `user.GetName()`
- Boolean methods: `Is`, `Has`, `Can` prefixes — `IsValid()`, `HasPermission()`

### Variables & constants

- Short variable names in small scopes: `i`, `n`, `ctx`, `err`
- Descriptive names in larger scopes: `userRepository`, `requestTimeout`
- Constants: `PascalCase` for exported, `camelCase` for unexported — NOT `UPPER_SNAKE_CASE`
- Error variables: `Err` prefix — `ErrNotFound`, `ErrUnauthorized`

### Interfaces

- Single-method interfaces: method name + `er` suffix — `Reader`, `Writer`, `Stringer`
- Multi-method interfaces: descriptive noun — `UserRepository`, `TokenValidator`
- Accept interfaces, return structs — depend on behavior, not implementation
- Keep interfaces small — prefer composition over large interfaces

```go

// ✅ Small, composable interfaces
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type ReadWriter interface {
    Reader
    Writer
}

// ✅ Domain interface — accept this in function signatures
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) error
}

```

---

## Error handling

### Core rules

- **Always handle errors** — never use `_` to discard an error unless explicitly justified with a comment
- **Wrap errors with context** using `fmt.Errorf` and `%w` verb
- **Check errors first** — guard clause pattern with early return
- **Never panic** in library code — panic is only acceptable in `main()` for unrecoverable startup failures

```go

// ✅ Wrap errors with context
user, err := s.repo.FindByID(ctx, id)
if err != nil {
    return nil, fmt.Errorf("find user %s: %w", id, err)
}

// ✅ Sentinel errors for expected conditions
var (
    ErrNotFound      = errors.New("not found")
    ErrUnauthorized  = errors.New("unauthorized")
    ErrAlreadyExists = errors.New("already exists")
)

// ✅ Check with errors.Is / errors.As
if errors.Is(err, ErrNotFound) {
    return http.StatusNotFound, nil
}

var validationErr *ValidationError
if errors.As(err, &validationErr) {
    return http.StatusBadRequest, validationErr.Fields()
}

```

### Custom error types

```go

// ✅ Custom error type with context
type AppError struct {
    Code    string
    Message string
    Err     error
}

func (e *AppError) Error() string {
    if e.Err != nil {
        return fmt.Sprintf("%s: %s: %v", e.Code, e.Message, e.Err)
    }
    return fmt.Sprintf("%s: %s", e.Code, e.Message)
}

func (e *AppError) Unwrap() error {
    return e.Err
}

```

---

## Project structure

### Standard layout

```

project/
├── cmd/
│   └── server/
│       └── main.go              # Entry point — minimal, wires dependencies
├── internal/                    # Private application code
│   ├── domain/                  # Domain models, interfaces, business rules
│   │   ├── user.go
│   │   └── order.go
│   ├── service/                 # Application services (use cases)
│   │   ├── user_service.go
│   │   └── user_service_test.go
│   ├── repository/              # Data access implementations
│   │   ├── postgres/
│   │   │   └── user_repo.go
│   │   └── redis/
│   │       └── cache.go
│   ├── handler/                 # HTTP/gRPC handlers
│   │   ├── user_handler.go
│   │   └── middleware/
│   │       ├── auth.go
│   │       └── logging.go
│   └── config/                  # Configuration loading
│       └── config.go
├── pkg/                         # Public reusable packages (use sparingly)
│   └── httputil/
│       └── response.go
├── api/                         # API contracts (OpenAPI, proto files)
│   └── proto/
│       └── user.proto
├── migrations/                  # Database migrations
├── go.mod
├── go.sum
├── Makefile
└── Dockerfile

```

### Rules

- `cmd/` contains only `main.go` files — wiring and startup, no business logic
- `internal/` for all private code — enforced by the Go compiler
- `pkg/` only for genuinely reusable packages — prefer `internal/` by default
- One package per directory — no multiple packages in the same folder
- Test files live next to the code they test: `user_service.go` + `user_service_test.go`
- Integration tests in a separate `_test` package: `package service_test`

---

## Concurrency

### Context

- **Every function that does I/O or may block must accept `context.Context` as its first parameter**
- Pass context down the call chain — never store it in a struct
- Use `context.WithTimeout`, `context.WithCancel` for lifecycle management
- Check `ctx.Err()` or `ctx.Done()` in long-running loops

```go

// ✅ Context as first parameter
func (s *UserService) FindByID(ctx context.Context, id string) (*User, error) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    return s.repo.FindByID(ctx, id)
}

```

### Goroutines & channels

- **Never launch a goroutine without a way to stop it** (context, done channel, or WaitGroup)
- Use `errgroup.Group` for concurrent tasks that may fail
- Prefer `sync.WaitGroup` for fire-and-forget concurrent work
- Channels for communication, mutexes for state — don't mix paradigms
- Buffered channels when producer and consumer have different speeds

```go

// ✅ errgroup for concurrent operations with error handling
func (s *Service) FetchAll(ctx context.Context, ids []string) ([]*User, error) {
    g, ctx := errgroup.WithContext(ctx)
    users := make([]*User, len(ids))

    for i, id := range ids {
        g.Go(func() error {
            user, err := s.repo.FindByID(ctx, id)
            if err != nil {
                return fmt.Errorf("fetch user %s: %w", id, err)
            }
            users[i] = user
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        return nil, err
    }
    return users, nil
}

```

### Common pitfalls

- Never use `go func()` in production without error recovery
- Always `defer cancel()` after `context.WithCancel` / `context.WithTimeout`
- Data races: use `-race` flag in tests — `go test -race ./...`
- Avoid goroutine leaks: ensure all goroutines terminate when the parent context is canceled

---

## Testing

### Table-driven tests — standard pattern

```go

func TestParseToken(t *testing.T) {
    tests := []struct {
        name    string
        input   string
        want    *Claims
        wantErr bool
    }{
        {
            name:  "valid token",
            input: "eyJhbGciOiJIUzI1NiIs...",
            want:  &Claims{UserID: "123", Role: "admin"},
        },
        {
            name:    "expired token",
            input:   "eyJhbGciOiJIUzI1NiIs...",
            wantErr: true,
        },
        {
            name:    "empty token",
            input:   "",
            wantErr: true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := ParseToken(tt.input)
            if tt.wantErr {
                require.Error(t, err)
                return
            }
            require.NoError(t, err)
            assert.Equal(t, tt.want, got)
        })
    }
}

```

### Testing rules

- Use `testify/require` for fatal assertions, `testify/assert` for non-fatal
- Test file: `*_test.go` in the same package (white-box) or `_test` package (black-box)
- Test function names: `Test<Function>_<scenario>` or table-driven with `name` field
- Use `t.Helper()` in test helper functions
- Use `t.Parallel()` when tests are independent
- Use `t.Cleanup()` instead of `defer` in tests for resource cleanup

### Benchmarks

```go

func BenchmarkParseToken(b *testing.B) {
    token := generateValidToken()
    b.ResetTimer()
    for b.Loop() {
        _, _ = ParseToken(token)
    }
}

```

### Test doubles

- Prefer interface-based mocking — define interfaces, provide test implementations
- Use `testify/mock` or hand-written fakes for complex interactions
- Never mock what you don't own — wrap third-party dependencies behind interfaces

---

## Linting & formatting

### golangci-lint — mandatory

```yaml

# .golangci.yml
linters:
  enable:
    - errcheck        # unchecked errors
    - govet           # suspicious constructs
    - staticcheck     # advanced static analysis
    - unused          # unused code
    - gosimple        # simplifications
    - ineffassign     # ineffective assignments
    - revive          # extensible linter (replaces golint)
    - gocritic        # opinionated checks
    - errorlint       # error wrapping issues
    - exhaustive      # exhaustive enum switches
    - noctx           # http requests without context
    - prealloc        # slice preallocation
    - bodyclose       # unclosed HTTP response bodies

linters-settings:
  revive:
    rules:
      - name: exported
        severity: warning
      - name: unexported-return
        severity: warning
  gocritic:
    enabled-tags:
      - diagnostic
      - style
      - performance

run:
  timeout: 5m

```

### Formatting

- `gofmt` is non-negotiable — all Go code must be formatted with `gofmt`
- `goimports` for automatic import organization — use as the default formatter
- No manual import grouping needed — `goimports` handles stdlib / third-party / local separation
- Run `golangci-lint run ./...` in CI — fail the build on any lint error

---

## Logging — structured with slog

### Standard library slog (Go 1.21+)

```go

import "log/slog"

// ✅ Initialize structured logger
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
}))
slog.SetDefault(logger)

// ✅ Structured log entries with context
slog.Info("user created",
    slog.String("user_id", user.ID),
    slog.String("email", user.Email),
    slog.Duration("latency", elapsed),
)

slog.Error("failed to create user",
    slog.String("user_id", req.UserID),
    slog.Any("error", err),
)

// ✅ Logger with pre-set attributes (correlation ID, request ID)
reqLogger := slog.With(
    slog.String("request_id", requestID),
    slog.String("trace_id", traceID),
)
reqLogger.Info("processing request")

```

### Rules

- Use `slog` (standard library) — no third-party logging libraries unless justified
- JSON format in production, text format in development
- Always include correlation/request ID in log entries
- Log at appropriate levels: `Debug` for development, `Info` for operations, `Warn` for recoverable issues, `Error` for failures
- Never log sensitive data (passwords, tokens, PII)

---

## Configuration

### Environment variables with Viper

```go

import "github.com/spf13/viper"

type Config struct {
    Port         int           `mapstructure:"PORT"`
    DatabaseURL  string        `mapstructure:"DATABASE_URL"`
    JWTSecret    string        `mapstructure:"JWT_SECRET"`
    ReadTimeout  time.Duration `mapstructure:"READ_TIMEOUT"`
    WriteTimeout time.Duration `mapstructure:"WRITE_TIMEOUT"`
    LogLevel     string        `mapstructure:"LOG_LEVEL"`
}

func LoadConfig() (*Config, error) {
    viper.AutomaticEnv()

    viper.SetDefault("PORT", 8080)
    viper.SetDefault("READ_TIMEOUT", 15*time.Second)
    viper.SetDefault("WRITE_TIMEOUT", 15*time.Second)
    viper.SetDefault("LOG_LEVEL", "info")

    var cfg Config
    if err := viper.Unmarshal(&cfg); err != nil {
        return nil, fmt.Errorf("unmarshal config: %w", err)
    }
    return &cfg, nil
}

```

### Rules

- Never hardcode configuration values — use environment variables
- Provide sensible defaults for non-sensitive settings
- Validate configuration at startup — fail fast on missing required values
- Use `mapstructure` tags for Viper binding
- Secrets (DB passwords, API keys, JWT secrets) come exclusively from environment or secret managers — never from config files

---

## API patterns

### HTTP server with graceful shutdown

```go

func main() {
    cfg, err := config.LoadConfig()
    if err != nil {
        slog.Error("failed to load config", slog.Any("error", err))
        os.Exit(1)
    }

    handler := setupRouter(cfg)

    srv := &http.Server{
        Addr:         fmt.Sprintf(":%d", cfg.Port),
        Handler:      handler,
        ReadTimeout:  cfg.ReadTimeout,
        WriteTimeout: cfg.WriteTimeout,
        IdleTimeout:  60 * time.Second,
    }

    // Start server in a goroutine
    go func() {
        slog.Info("server starting", slog.Int("port", cfg.Port))
        if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
            slog.Error("server failed", slog.Any("error", err))
            os.Exit(1)
        }
    }()

    // Wait for interrupt signal
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    slog.Info("server shutting down")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        slog.Error("server forced shutdown", slog.Any("error", err))
        os.Exit(1)
    }

    slog.Info("server stopped")
}

```

### Middleware pattern

```go

// ✅ Standard middleware signature
type Middleware func(http.Handler) http.Handler

func RequestIDMiddleware() Middleware {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            requestID := r.Header.Get("X-Request-ID")
            if requestID == "" {
                requestID = uuid.New().String()
            }
            ctx := context.WithValue(r.Context(), requestIDKey, requestID)
            w.Header().Set("X-Request-ID", requestID)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}

func LoggingMiddleware(logger *slog.Logger) Middleware {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()
            wrapped := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}
            next.ServeHTTP(wrapped, r)
            logger.Info("request completed",
                slog.String("method", r.Method),
                slog.String("path", r.URL.Path),
                slog.Int("status", wrapped.statusCode),
                slog.Duration("latency", time.Since(start)),
            )
        })
    }
}

// ✅ Chain middleware
func Chain(h http.Handler, middlewares ...Middleware) http.Handler {
    for i := len(middlewares) - 1; i >= 0; i-- {
        h = middlewares[i](h)
    }
    return h
}

```

### JSON response helpers

```go

func writeJSON(w http.ResponseWriter, status int, data any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    if err := json.NewEncoder(w).Encode(data); err != nil {
        slog.Error("failed to encode response", slog.Any("error", err))
    }
}

func writeError(w http.ResponseWriter, status int, message string) {
    writeJSON(w, status, map[string]string{"error": message})
}

```

---

## Security

### Input validation

- Validate all inputs at the handler level before passing to services
- Use a validation library (`go-playground/validator`) or hand-written checks
- Reject unknown fields in JSON payloads (`DisallowUnknownFields`)
- Limit request body size with `http.MaxBytesReader`

```go

// ✅ Limit and validate request body
func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
    r.Body = http.MaxBytesReader(w, r.Body, 1<<20) // 1 MB limit

    decoder := json.NewDecoder(r.Body)
    decoder.DisallowUnknownFields()

    var req CreateUserRequest
    if err := decoder.Decode(&req); err != nil {
        writeError(w, http.StatusBadRequest, "invalid request body")
        return
    }

    if err := h.validator.Struct(req); err != nil {
        writeError(w, http.StatusBadRequest, err.Error())
        return
    }

    // ... proceed with validated input
}

```

### Crypto & secrets

- Use `crypto/rand` for random values — never `math/rand` for security-sensitive code
- Hash passwords with `golang.org/x/crypto/bcrypt` or `argon2`
- Use `crypto/subtle.ConstantTimeCompare` for timing-safe comparisons
- Never log secrets, tokens, or passwords

### TLS & HTTP security

- Always set `ReadTimeout`, `WriteTimeout`, `IdleTimeout` on `http.Server`
- Set security headers: `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`
- Use `crypto/tls` with `tls.Config{MinVersion: tls.VersionTLS12}`
- Sanitize user-generated content before rendering

### SQL injection prevention

- Always use parameterized queries — never concatenate user input into SQL
- Use `database/sql` placeholders: `db.Query("SELECT * FROM users WHERE id = $1", id)`
- Prefer an ORM or query builder (`sqlx`, `sqlc`) for complex queries
