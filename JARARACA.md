# Python Development Standards & Guidelines v0.1.b

## 1. Code Architecture & Design Principles

### SOLID Principles
- **Single Responsibility**: Each class or module should have only one reason to change
- **Open-Closed**: Software entities should be open for extension but closed for modification
- **Liskov Substitution**: Objects should be replaceable with instances of their subtypes
- **Interface Segregation**: Many specific interfaces are better than one general interface
- **Dependency Inversion**: Depend on abstractions, not concrete implementations

### SOLID Principles with Examples

#### Single Responsibility
```python
# ✅ GOOD: Class has single responsibility
class EmailSender:
    def send_email(self, recipient: str, subject: str, body: str) -> None:
        # Email sending logic here
        pass

# ❌ BAD: Class has multiple responsibilities
class UserManager:
    def create_user(self, username: str, password: str) -> int:
        # User creation logic
        pass
    
    def send_welcome_email(self, user: dict) -> bool:
        # Email sending logic
        pass
    
    def generate_user_report(self, user: dict) -> str:
        # Report generation logic
        pass
```

#### Open-Closed
```python
# ✅ GOOD: Open for extension, closed for modification
class PaymentProcessor:
    def process_payment(self, payment: "PaymentMethod") -> None:
        payment.process()

class CreditCardPayment:
    def process(self) -> None:
        # Credit card specific logic

class PayPalPayment:
    def process(self) -> None:
        # PayPal specific logic

# ❌ BAD: Requires modification for new payment types
class PaymentProcessor:
    def process_payment(self, payment_type: str, amount: float) -> None:
        if payment_type == "credit_card":
            # Credit card logic
        elif payment_type == "paypal":
            # PayPal logic
        # Adding a new payment type requires modifying this method
```

#### Liskov Substitution
```python
# ✅ GOOD: Square can substitute Rectangle without breaking behavior
class Rectangle:
    def __init__(self, width: float, height: float) -> None:
        self._width = width
        self._height = height

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        self._width = value

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        self._height = value

    def area(self) -> float:
        return self.width * self.height

class Square(Rectangle):
    def __init__(self, side: float) -> None:
        super().__init__(side, side)

# ❌ BAD: Violates LSP by changing setter behavior
class BadSquare(Rectangle):
    def __init__(self, side: float) -> None:
        super().__init__(side, side)

    @Rectangle.width.setter
    def width(self, value: float) -> None:
        self._width = value
        self._height = value  # Breaks rectangle invariants

    @Rectangle.height.setter
    def height(self, value: float) -> None:
        self._width = value
        self._height = value
```

#### Interface Segregation
```python
# ✅ GOOD: Specific interfaces for different clients
from abc import ABC, abstractmethod

class Printer(ABC):
    @abstractmethod
    def print_document(self, document: str) -> bool:
        pass

class Scanner(ABC):
    @abstractmethod
    def scan_document(self) -> bytes:
        pass

class MultiFunctionPrinter(Printer, Scanner):
    def print_document(self, document: str) -> bool:
        # Print implementation
        return True
    
    def scan_document(self) -> bytes:
        # Scan implementation
        return b"scanned_content"

class BasicPrinter(Printer):
    def print_document(self, document: str) -> bool:
        # Print implementation
        return True

# ❌ BAD: One large interface that forces clients to depend on methods they don't use
class AllInOneMachine(ABC):
    @abstractmethod
    def print_document(self, document: str) -> bool:
        pass
    
    @abstractmethod
    def scan_document(self) -> bytes:
        pass
    
    @abstractmethod
    def fax_document(self, document: str, recipient: str) -> bool:
        pass
    
    @abstractmethod
    def copy_document(self) -> bytes:
        pass
```

#### Dependency Inversion
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

# ✅ GOOD: High-level module depends on abstraction
class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: float) -> Dict[str, Any]:
        pass

class StripeGateway(PaymentGateway):
    def charge(self, amount: float) -> Dict[str, Any]:
        # Stripe-specific implementation
        return {"status": "success", "id": "tx123"}

class PaymentProcessor:
    def __init__(self, gateway: PaymentGateway):  # Depends on abstraction
        self.gateway = gateway

# ❌ BAD: High-level module depends on concrete implementation
class DirectStripeProcessor:
    def __init__(self):
        self.stripe_api = StripeAPI()  # Direct dependency on concrete class
    
    def process_payment(self, amount: float) -> None:
        self.stripe_api.charge(amount)
```

### Common Design Patterns

#### Factory Pattern
```python
from abc import ABC, abstractmethod
from typing import Dict, Type, Callable, List, Optional

class PaymentMethod(ABC):
    @abstractmethod
    def process(self) -> None:
        pass
        
    @abstractmethod
    def validate(self) -> bool:
        """Validate the payment method before processing."""
        pass

class PaymentFactory:
    _registry: Dict[str, Type[PaymentMethod]] = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        def decorator(payment_cls: Type[PaymentMethod]) -> Type[PaymentMethod]:
            cls._registry[name] = payment_cls
            return payment_cls
        return decorator

    @classmethod
    def create(cls, name: str, **kwargs) -> PaymentMethod:
        if name not in cls._registry:
            raise ValueError(f"Unsupported payment type: {name}")
        return cls._registry[name](**kwargs)

@PaymentFactory.register("credit_card")
class CreditCardPayment(PaymentMethod):
    def __init__(self, card_number: str, expiry: str, cvv: str):
        self.card_number = card_number
        self.expiry = expiry
        self.cvv = cvv
        
    def validate(self) -> bool:
        # Validate card details
        return len(self.card_number) == 16 and len(self.cvv) == 3
        
    def process(self) -> None:
        if not self.validate():
            raise ValueError("Invalid credit card details")
        print("Processing credit card payment")

@PaymentFactory.register("paypal")
class PayPalPayment(PaymentMethod):
    def __init__(self, email: str, token: Optional[str] = None):
        self.email = email
        self.token = token
        
    def validate(self) -> bool:
        # Validate PayPal details
        return "@" in self.email
        
    def process(self) -> None:
        if not self.validate():
            raise ValueError("Invalid PayPal details")
        print("Processing PayPal payment")

# Usage
credit_card = PaymentFactory.create(
    "credit_card", 
    card_number="4111111111111111", 
    expiry="12/25", 
    cvv="123"
)
credit_card.process()

paypal = PaymentFactory.create("paypal", email="customer@example.com")
paypal.process()
```

#### Singleton Pattern
```python
from typing import Optional, Dict, Any
import threading

# Method 1: Using a metaclass
class Singleton(type):
    _instances: Dict[Any, Any] = {}
    _lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class DatabaseConnection(metaclass=Singleton):
    def __init__(self, connection_string: str = "default"):
        self.connection_string = connection_string
        # Initialize connection...
        
    def query(self, sql: str) -> list:
        # Execute query...
        return []
        
# Method 2: Using a module-level instance (Pythonic way)
# In database.py
_db_instance: Optional[DatabaseConnection] = None

def get_database() -> DatabaseConnection:
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnection("production")
    return _db_instance

# Method 3: Borg pattern (shared state)
class BorgDatabase:
    _shared_state: Dict[str, Any] = {}
    
    def __init__(self):
        self.__dict__ = self._shared_state
        if not self._shared_state:
            self.connection_string = "default"
            # Initialize only once...
```

#### Decorator Pattern
```python
from functools import wraps
from typing import Callable, Any, TypeVar

T = TypeVar('T')

# Function decorator example
def log_execution(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        print(f"Executing {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Completed {func.__name__}")
        return result
    return wrapper

@log_execution
def process_data(data: list) -> list:
    return [item * 2 for item in data]

# Class decorator example
class AuthorizationDecorator:
    def __init__(self, component):
        self._component = component
        
    def operation(self, user_id: int) -> str:
        if self._check_access(user_id):
            return self._component.operation()
        return "Access denied"
        
    def _check_access(self, user_id: int) -> bool:
        # Authorization logic
        return user_id > 0
```

## 2. File & Folder Naming Conventions

### Files & Modules
- Use `snake_case` for all files (e.g., `user_authentication.py`, `data_processor.py`)
- Make names descriptive and action-oriented (e.g., `fetch_user_data.py`, `process_transactions.py`)
- Include design pattern indicators when applicable (e.g., `singleton_logger.py`, `factory_payment.py`)
- Avoid generic names like `utils.py` or `helpers.py` without qualification
- For acronyms in modules, use lowercase (e.g., `html_parser.py`, `json_serializer.py`)

### Classes, Functions & Variables
- **Classes**: Use `PascalCase` (e.g., `UserAuthentication`, `OrderProcessor`)
- **Functions/Methods**: Use `snake_case` (e.g., `calculate_total`, `validate_input`)
- **Variables**: Use `snake_case` with descriptive names (e.g., `user_count`, `active_sessions`)
- **Constants**: Use `UPPER_CASE` (e.g., `MAX_RETRIES`, `API_TIMEOUT`)
- **Acronyms in class names**: Capitalize only the first letter (e.g., `HtmlParser`, `JsonWriter`) for readability, not `HTMLParser`

### Package Naming
- Use `snake_case` for package names (e.g., `payment_processing`, `data_analysis`)
- Avoid package names that conflict with standard library or common third-party packages
- Prefer shorter names for deeper package hierarchies

### Files & Modules Examples

```
# ✅ GOOD naming examples:
fetch_user_data.py        # Clear action (fetch) and subject (user data)
process_payment_service.py # Descriptive of functionality
singleton_database.py     # Includes design pattern
user_authentication.py    # Clear purpose
oauth_client.py           # Acronym (OAuth) in lowercase for modules

# ❌ BAD naming examples:
utils.py                  # Too generic
stuff.py                  # Meaningless
do_things.py              # Vague
helper.py                 # Not specific enough
HTMLParser.py             # Incorrect capitalization for file
```

### Classes, Functions & Variables Examples

```python
# ✅ GOOD examples
class UserAuthentication:  # PascalCase for classes
    
    MAX_LOGIN_ATTEMPTS = 5  # UPPER_CASE for constants
    
    def __init__(self, username: str):
        self.username = username  # snake_case for variables
        self.login_attempts = 0
    
    def validate_credentials(self, password: str) -> bool:  # snake_case for methods
        # Validation logic
        return True

class HtmlParser:  # Acronym with only first letter capitalized
    def parse_document(self, content: str) -> dict:
        # Parsing logic
        return {}

# ❌ BAD examples
class user_auth:  # Should be PascalCase
    
    maxLoginAttempts = 5  # Should be UPPER_CASE
    
    def __init__(self, UserName):  # Inconsistent naming
        self.UserName = UserName  # Should be snake_case
    
    def ValidateUser(self, pwd):  # Should be snake_case
        # Logic
        pass

class HTMLParser:  # All-caps acronym reduces readability
    pass
```

### Project Structure
```
project/
  ├── src/
  │    ├── models/           # Data models and entities
  │    ├── services/         # Business logic
  │    ├── interfaces/       # Abstract interfaces
  │    ├── views/            # UI/presentation components
  │    ├── routes/           # API endpoints/routes
  │    └── exceptions/       # Custom exception classes
  ├── tests/
  ├── docs/
  └── config/
```

### Project Structure Example
```
ecommerce_project/
  ├── src/
  │    ├── models/
  │    │    ├── user.py                  # User data model
  │    │    ├── product.py               # Product data model
  │    │    └── order.py                 # Order data model
  │    │
  │    ├── services/
  │    │    ├── authentication_service.py # User auth business logic
  │    │    ├── order_processor.py        # Order processing logic
  │    │    └── payment_service.py        # Payment processing
  │    │
  │    ├── interfaces/
  │    │    ├── payment_provider.py       # Payment gateway interface
  │    │    └── notification_service.py    # Notification interface
  │    │
  │    ├── views/
  │    │    ├── user_dashboard.py         # User dashboard UI
  │    │    └── product_catalog.py        # Product listing UI
  │    │
  │    ├── routes/
  │    │    ├── user_routes.py            # User API endpoints
  │    │    └── order_routes.py           # Order API endpoints
  │    │
  │    └── exceptions/
  │         ├── auth_exceptions.py         # Authentication errors
  │         └── payment_exceptions.py      # Payment processing errors
  │
  ├── tests/
  │    ├── test_user_model.py
  │    └── test_order_service.py
  │
  ├── docs/
  │    └── api_documentation.md
  │
  └── config/
       └── settings.py
```

### Common Directories
```
project/
  ├── src/
  │    ├── core/            # Foundational domain logic
  │    ├── infrastructure/  # External integrations
  │    ├── api/             # Web API components
  │    └── ...             
  ├── scripts/             # Maintenance/DB scripts
  ├── migrations/          # Database migration files
  └── ...
```

## 3. Code Organization

- **Maximum File Length**: 300 lines of code - refactor longer files
  - *Exception*: Generated files (e.g., migrations, protobuf) may exceed this limit
  - *Exception*: Files with extensive documentation or test data
- **Function Length**: Keep functions under 50 lines
- **Module Organization**: Group related functionality together
- **Import Order**: Standard library → Third-party → Local modules

### Module Organization Guidelines
- Use `__init__.py` to expose public API of packages
- Prefer many small files over few large ones
- Keep related test files mirroring source structure
- Separate infrastructure code from business logic
- Use `if __name__ == "__main__":` guard for script execution
```python
# Example of a well-organized module's __init__.py
from .auth_service import authenticate_user, create_user
from .exceptions import AuthenticationError

__all__ = ['authenticate_user', 'create_user', 'AuthenticationError']
```

### Import Organization

```python
# ✅ GOOD: Organized imports
# Standard library imports
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Third-party imports
import pandas as pd
import requests
from flask import Flask, jsonify, request

# Local imports
from .models import User
from .services import authenticate
from .utils.date_helpers import format_timestamp

# ❌ BAD: Disorganized imports
import requests
from .models import User
import os
from flask import Flask, jsonify, request
import pandas as pd
from datetime import datetime
```

### Function Length & Complexity

```python
# ✅ GOOD: Focused function under 50 lines
from typing import List, Dict, Optional, Union

def calculate_order_total(order_items: List["OrderItem"], discount_code: Optional[str] = None) -> Dict[str, float]:
    """Calculate the total price of an order with any applicable discounts."""
    subtotal = sum(item.price * item.quantity for item in order_items)
    
    discount = 0.0
    if discount_code:
        discount = apply_discount(subtotal, discount_code)
    
    tax = calculate_tax(subtotal - discount)
    
    return {
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": subtotal - discount + tax
    }

# ❌ BAD: Long function with multiple responsibilities
def process_order(user_id: int, items: List[Dict], shipping_address: Dict, 
                  payment_info: Dict, discount_code: Optional[str] = None) -> Dict:
    # 100+ lines of code handling:
    # - User validation
    # - Inventory checks
    # - Price calculation
    # - Discount application
    # - Tax calculation
    # - Payment processing
    # - Order creation
    # - Email notification
    # - Too many responsibilities in one function!
```

## 4. Python Best Practices

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Write comprehensive docstrings per [PEP 257](https://www.python.org/dev/peps/pep-0257/)
- Use type hints for function parameters and return values
- Leverage established design patterns appropriately
- Use f-strings for string interpolation

### F-String Examples

```python
# ✅ GOOD: Using f-strings for readability and performance
name = "Alice"
age = 30
message = f"Hello, {name}! You are {age} years old."

# Calculate values in f-strings
total = 42.5567
output = f"Total: ${total:.2f}"  # "Total: $42.56"

# Format datetimes
from datetime import datetime
now = datetime.now()
formatted = f"Current time: {now:%Y-%m-%d %H:%M:%S}"

# ❌ BAD: Older string formatting methods
message = "Hello, %s! You are %d years old." % (name, age)  # %-formatting
message = "Hello, {}! You are {} years old.".format(name, age)  # str.format()
```

### Type Hints Example

```python
from typing import List, Dict, Optional, Union, TypedDict, Callable

# Basic type hints
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Complex type hints
class UserData(TypedDict):
    id: int
    name: str
    email: str
    active: bool

def get_active_users(
    department: str, 
    status: Optional[str] = None,
    transform_func: Optional[Callable[[UserData], Dict]] = None
) -> List[UserData]:
    """
    Retrieve active users from the specified department.
    
    Args:
        department: The department to filter users by
        status: Optional status filter
        transform_func: Optional function to transform each user record
        
    Returns:
        A list of user dictionaries with user details
    """
    # Implementation here
    users: List[UserData] = []
    return users
```

### Data Validation with Pydantic

Pydantic enforces type hints at runtime, providing data validation, serialization, and documentation capabilities.

```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator

class UserBase(BaseModel):
    """Base user data model with validation."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    is_active: bool = True
    
    # Custom validators
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():  # Allows underscores
            raise ValueError('must be alphanumeric (underscores allowed)')
        if len(v) < 4:
            raise ValueError('must be at least 4 characters')
        return v

class UserCreate(UserBase):
    """User creation model with password requirements."""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('must contain at least one uppercase letter')
        return v

class User(UserBase):
    """Complete user model with system fields."""
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True  # For ORM compatibility

# Example usage
try:
    user = UserCreate(
        username="john@doe",  # Contains invalid character
        email="john@example.com",
        password="Weakpwd123"
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

### Configuration Management with Pydantic

```python
from pydantic import BaseSettings, Field
from typing import Optional

class DatabaseSettings(BaseSettings):
    """Database configuration with environment variable support."""
    host: str = Field("localhost", env="DB_HOST")
    port: int = Field(5432, env="DB_PORT")
    username: str = Field(..., env="DB_USER")
    password: str = Field(..., env="DB_PASSWORD")
    database: str = Field(..., env="DB_NAME")
    
    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    class Config:
        env_file = ".env"  # Load from .env file

class AppSettings(BaseSettings):
    """Application settings."""
    app_name: str = "My Application"
    debug: bool = False
    database: DatabaseSettings = DatabaseSettings()
    secret_key: str = Field(..., env="SECRET_KEY")
    
    class Config:
        env_nested_delimiter = "__"  # For nested settings in env vars

# Usage
settings = AppSettings()
print(f"Connecting to: {settings.database.connection_string}")
```

## 5. Asynchronous Best Practices

- Use `async` and `await` for non-blocking I/O operations
- Avoid running blocking calls inside async functions
- Use `asyncio.run()` as an entry point for asynchronous execution
- Consider `aiohttp` for async HTTP requests instead of `requests`
- Prefer `asyncio.create_task()` for scheduling background tasks

### When to use `asyncio.create_task()` vs `asyncio.gather()`

```python
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional

# Use asyncio.create_task() when:
# - You want to start a task and continue execution immediately
# - Tasks are independent and don't need to be awaited together
# - You need to fire-and-forget tasks (with proper cleanup)

async def fire_and_forget_example() -> None:
    """Example of creating background tasks that run independently."""
    async def background_job(name: str) -> None:
        print(f"Starting {name}")
        await asyncio.sleep(2)
        print(f"Finished {name}")
    
    # Start tasks without immediately awaiting them
    task1 = asyncio.create_task(background_job("job1"))
    task2 = asyncio.create_task(background_job("job2"))
    
    print("Main function continues while tasks run in background")
    
    # Ensure tasks complete before function exits
    await task1
    await task2

# Use asyncio.gather() when:
# - You need to wait for all tasks to complete before continuing
# - You want to collect all results together
# - You want to handle exceptions from all tasks

async def gather_example() -> List[Dict[str, Any]]:
    """Example of running multiple tasks concurrently and collecting results."""
    async def fetch_user_data(user_id: int) -> Optional[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.example.com/users/{user_id}") as response:
                if response.status == 200:
                    return await response.json()
                return None
    
    # Run all tasks concurrently and wait for all to complete
    user_ids = [1, 2, 3, 4, 5]
    results = await asyncio.gather(
        *[fetch_user_data(user_id) for user_id in user_ids],
        return_exceptions=True  # Prevents one failed task from causing all to fail
    )
    
    # Filter out exceptions or None results
    valid_results = [r for r in results if isinstance(r, dict)]
    return valid_results
```

### Graceful Shutdown and Exception Handling

```python
import asyncio
import signal
from typing import Set, Callable, Any, Coroutine

class AsyncApp:
    def __init__(self):
        self.tasks: Set[asyncio.Task] = set()
        self._shutdown_requested = False
        
    async def startup(self) -> None:
        """Initialize resources and start background tasks."""
        # Setup signal handlers for graceful shutdown
        for sig in (signal.SIGINT, signal.SIGTERM):
            asyncio.get_event_loop().add_signal_handler(
                sig, lambda s=sig: asyncio.create_task(self.shutdown(s))
            )
        
        # Start background tasks
        self.tasks.add(asyncio.create_task(self.background_task()))
        print("Application started")
        
    async def shutdown(self, signal: Optional[signal.Signals] = None) -> None:
        """Gracefully shutdown the application."""
        if self._shutdown_requested:
            return
            
        self._shutdown_requested = True
        print(f"Shutdown requested (signal: {signal.name if signal else 'manual'})")
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
            
        # Wait for all tasks to complete with a timeout
        await asyncio.gather(*self.tasks, return_exceptions=True)
        print("All tasks have been cancelled")
        
        # Close other resources (DB connections, etc.)
        # await self.db.close()
        
        print("Shutdown complete")
        
    async def background_task(self) -> None:
        """Example background task with exception handling."""
        try:
            while not self._shutdown_requested:
                print("Background task running...")
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            # Handle task cancellation
            print("Background task cancelled, cleaning up...")
            # Cleanup code here
            raise  # Re-raise to properly mark the task as cancelled
        except Exception as e:
            print(f"Background task encountered an error: {e}")
            # Log the error, potentially restart the task
            
    async def run(self) -> None:
        """Main entry point."""
        await self.startup()
        try:
            # Keep the application running
            while not self._shutdown_requested:
                await asyncio.sleep(1)
        finally:
            # Ensure shutdown happens even if an exception occurred
            await self.shutdown()

# Usage
if __name__ == "__main__":
    app = AsyncApp()
    asyncio.run(app.run())
```

## 6. Testing & Quality Assurance

- Aim for minimum 80% code coverage
- Implement integration tests for component interactions
- Use fixtures and mocks to isolate test dependencies
- Write unit tests for all significant functionality
- Follow consistent test naming conventions

### Test Naming Conventions

```
test_[unit_under_test]_[scenario]_[expected_outcome]
```

For example:
- `test_user_registration_with_valid_data_succeeds`
- `test_login_with_incorrect_password_fails`
- `test_order_calculation_with_empty_cart_returns_zero`

### Testing Examples
```python
# ✅ GOOD: Clear, focused unit test with proper naming
import unittest
from unittest.mock import MagicMock
from services.payment_service import PaymentProcessor

class TestPaymentProcessor(unittest.TestCase):
    def setUp(self):
        self.payment_gateway = MagicMock()
        self.processor = PaymentProcessor(self.payment_gateway)
    
    def test_process_payment_with_valid_card_succeeds(self):
        # Arrange
        self.payment_gateway.charge.return_value = {"status": "success", "id": "tx123"}
        payment_details = {"amount": 100, "card_number": "4111111111111111"}
        
        # Act
        result = self.processor.process_payment(payment_details)
        
        # Assert
        self.assertTrue(result.is_successful)
        self.payment_gateway.charge.assert_called_once_with(100, "4111111111111111")
    
    def test_process_payment_with_insufficient_funds_fails(self):
        # Arrange
        self.payment_gateway.charge.return_value = {"status": "declined", "reason": "insufficient_funds"}
        payment_details = {"amount": 100, "card_number": "4111111111111111"}
        
        # Act
        result = self.processor.process_payment(payment_details)
        
        # Assert
        self.assertFalse(result.is_successful)
        self.assertEqual(result.error_message, "Payment declined: insufficient_funds")
```

### Coverage Tools Integration

```python
# Coverage configuration in pyproject.toml
"""
[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "**/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "pass",
    "raise ImportError"
]
fail_under = 80
"""

# Running tests with coverage
"""
# Command line
python -m pytest --cov=src --cov-report=term-missing

# GitHub Actions workflow example
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      - name: Test with pytest and coverage
        run: |
          python -m pytest --cov=src --cov-report=xml
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
"""
```

#### Example with Pytest Parameterization
```python
import pytest
from app.calculations import square

@pytest.mark.parametrize(
    "input_value, expected_result",
    [
        (5, 25),
        (0, 0),
        (-3, 9),
        (1.5, 2.25),
    ],
    ids=["positive_integer", "zero", "negative_number", "decimal"]
)
def test_square_function_calculates_correctly(input_value, expected_result):
    assert square(input_value) == expected_result
```

## 7. Code Maintainability

- Document complex algorithms and business rules
- Review code regularly
- Use automated linting and formatting tools
- Keep dependencies updated and documented

### Conventional Commits

Following the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common types:
- `feat:` - A new feature
- `fix:` - A bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code changes that neither fix bugs nor add features
- `perf:` - Performance improvements
- `test:` - Adding or fixing tests
- `chore:` - Routine tasks, dependency updates, etc.

Examples:
```
feat(auth): implement JWT authentication
fix(orders): correct tax calculation for international orders
docs: update API documentation with new endpoints
refactor(payment): extract payment validation to separate module
```

Benefits:
- Automated generation of changelogs
- Automated semantic versioning
- Clear communication of changes
- Easier to filter and search through commit history

### Proper Docstrings

```python
def calculate_shipping_cost(package_weight: float, destination_zip: str, expedited: bool = False) -> float:
    """
    Calculate the shipping cost for a package based on weight and destination.
    
    Args:
        package_weight (float): Weight of the package in pounds
        destination_zip (str): Destination ZIP code
        expedited (bool, optional): Whether expedited shipping is requested. Defaults to False.
    
    Returns:
        float: The calculated shipping cost in dollars
        
    Raises:
        ValueError: If package_weight is negative or destination_zip is invalid
    
    Example:
        >>> calculate_shipping_cost(2.5, "94043")
        8.50
        >>> calculate_shipping_cost(2.5, "94043", expedited=True)
        12.75
    """
    # Implementation here
```

## 8. Error Handling, Logging & Monitoring Best Practices

- Use structured logging instead of `print`
- Use different log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- Never log sensitive information (passwords, tokens, PII)
- Use specific exceptions instead of bare `except:` clauses
- Create custom exception classes for domain errors
- Include context in exceptions (e.g., "Failed to process order {id}")
- Clean up resources using `finally` or context managers

### Advanced Logging Configuration

```python
# Using dictConfig for flexible logging configuration
import logging
import logging.config
import structlog
import json
from typing import Dict, Any

# Configure standard logging with dictConfig
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "json": {
            "format": "%(message)s",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": "app.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
            "level": "DEBUG",
        },
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
        "app": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        # Third-party loggers can be configured here
        "requests": {
            "level": "WARNING",
            "propagate": True,
        },
    },
}

logging.config.dictConfig(logging_config)
logger = logging.getLogger("app")

# Structured logging with structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

structured_logger = structlog.get_logger()

# Usage examples
def process_request(request_id: str, user_id: str, data: Dict[str, Any]) -> None:
    # Basic logging
    logger.info(f"Processing request {request_id} for user {user_id}")
    
    # Structured logging
    structured_logger.info(
        "request_processing", 
        request_id=request_id, 
        user_id=user_id,
        data_size=len(json.dumps(data))
        # NEVER log the full data object if it might contain sensitive information
    )
    
    try:
        # Process the request...
        result = complex_operation(data)
        logger.debug(f"Operation result: {result}")
    except ValueError as e:
        logger.warning(f"Invalid data in request {request_id}: {e}")
        # Re-raise with context
        raise ValueError(f"Cannot process request {request_id}: {e}") from e
    except Exception as e:
        # Log the error with full traceback
        logger.exception(f"Failed to process request {request_id}")
        # This is equivalent to:
        # logger.error(f"Failed to process request {request_id}", exc_info=True)
        raise
```

### Monitoring Integration

```python
# Sentry integration
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1,  # Adjust sampling rate based on traffic
    environment="production",
)

# Prometheus metrics (using Flask example)
from flask import Flask
from prometheus_client import Counter, Histogram, generate_latest
import time

app = Flask(__name__)

# Define metrics
REQUEST_COUNT = Counter(
    'request_count', 'App Request Count',
    ['app_name', 'method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'request_latency_seconds', 'Request latency',
    ['app_name', 'endpoint']
)

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain'}

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    request_latency = time.time() - request.start_time
    REQUEST_LATENCY.labels('webapp', request.path).observe(request_latency)
    REQUEST_COUNT.labels('webapp', request.method, request.path, response.status_code).inc()
    return response
```

## 9. Security Best Practices

- Never store sensitive information in code or version control
- Use environment variables for secrets and configuration
- Use secure password hashing algorithms (bcrypt, Argon2)
- Implement proper input validation and sanitization
- Use parameterized queries to prevent SQL injection
- Enable HTTPS/TLS for all external communication
- Implement proper authentication and authorization
- Use rate limiting for public APIs to prevent abuse
- Keep dependencies updated to avoid known vulnerabilities
- Perform regular security audits and penetration testing
- Apply the principle of least privilege
- Never log sensitive information

### Password Security Example

```python
import bcrypt
import os
from dotenv import load_dotenv
from passlib.hash import argon2  # Another strong hashing algorithm

# Load secrets from environment variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

def hash_password(password: str) -> str:
    """Securely hash a password using bcrypt."""
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# Alternative using Argon2 (considered more secure)
def hash_password_argon2(password: str) -> str:
    """Hash a password using Argon2."""
    return argon2.hash(password)

def verify_password_argon2(password: str, hashed_password: str) -> bool:
    """Verify a password against an Argon2 hash."""
    return argon2.verify(password, hashed_password)

def register_user(username: str, password: str) -> int:
    """Register a new user with secure password storage."""
    # Input validation (minimal example)
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
        
    # Hash the password before storing
    hashed_password = hash_password(password)
    
    # Store in database using parameterized query
    # Example with SQLAlchemy:
    # user = User(username=username, password_hash=hashed_password)
    # db.session.add(user)
    # db.session.commit()
    # return user.id
    return 1  # Placeholder
```

### JWT Authentication Example

```python
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

def create_access_token(
    user_id: int, 
    expires_delta: timedelta = timedelta(minutes=15),
    secret_key: str = os.getenv("SECRET_KEY")
) -> str:
    """Create a JWT access token."""
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt

def decode_token(
    token: str, 
    secret_key: str = os.getenv("SECRET_KEY")
) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None
```

### Principle of Least Privilege

```python
# Database access with minimal privileges
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_read_only_session():
    """Create a database session with read-only privileges."""
    # Connect with a read-only user
    read_engine = create_engine(os.getenv("READ_ONLY_DB_URL"))
    ReadSession = sessionmaker(bind=read_engine)
    return ReadSession()

def get_admin_session():
    """Create a database session with admin privileges."""
    # Only used for specific administrative tasks
    admin_engine = create_engine(os.getenv("ADMIN_DB_URL"))
    AdminSession = sessionmaker(bind=admin_engine)
    return AdminSession()

# Example of API key with limited scope
class ApiKey:
    def __init__(self, key: str, scopes: List[str]):
        self.key = key
        self.scopes = scopes
    
    def has_permission(self, required_scope: str) -> bool:
        """Check if the API key has the required scope."""
        return required_scope in self.scopes

def authorize_api_request(api_key: str, required_scope: str) -> bool:
    """Authorize an API request based on scope."""
    key_data = get_api_key_from_db(api_key)
    if not key_data:
        return False
    
    api_key_obj = ApiKey(key_data["key"], key_data["scopes"])
    return api_key_obj.has_permission(required_scope)
```

### Preventing SQL Injection

```python
# ✅ GOOD: Using parameterized queries
def get_user(user_id: int) -> Optional[Dict]:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()

# ❌ BAD: String formatting or concatenation in SQL queries
def get_user_unsafe(user_id: int) -> Optional[Dict]:
    cursor = connection.cursor()
    # VULNERABLE to SQL injection!
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()
```

## 10. Dependency Management

- Use **virtual environments** (`venv`, `poetry`, or `pipenv`)
- Pin dependencies using `requirements.txt` or `pyproject.toml`
- Regularly update dependencies with `pip-audit` or `safety`
- Use dependency lockfiles for reproducible builds
- Consider Docker containers for consistent development environments
- Add dependency checking to CI/CD pipelines

### Virtual Environment Setup Example

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate requirements file
pip freeze > requirements.txt

# Check for security vulnerabilities
pip install pip-audit
pip-audit
```

### Poetry Example

```bash
# Initialize a new project
poetry new my_project

# Add dependencies
poetry add requests flask

# Add development dependencies
poetry add --dev pytest black flake8

# Install dependencies
poetry install

# Update dependencies
poetry update

# Export requirements.txt
poetry export -f requirements.txt --output requirements.txt
```

### Docker with Dependency Lock

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . .

CMD ["python", "-m", "app.main"]
```

### CI/CD Dependency Checking

```yaml
# GitHub Actions workflow
name: Dependency Check

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Run weekly

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pip-audit safety
      - name: Check dependencies with pip-audit
        run: |
          pip-audit -r requirements.txt
      - name: Check dependencies with safety
        run: |
          safety check -r requirements.txt
```

## 11. Performance Awareness

- Prefer generators for large datasets
- Use `lru_cache` for expensive pure functions
- Avoid premature optimization
- Profile before optimizing (`cProfile`, `py-spy`)
- Consider time complexity for algorithms
- Use connection pooling for databases
- Understand appropriate concurrency models

### Concurrency Models

```python
# Example: Choosing the right concurrency model

# 1. Multi-threading - Good for I/O-bound tasks
import threading
import queue
import time

def threaded_download(urls: List[str]) -> List[str]:
    """Download multiple URLs using threading."""
    results = []
    result_lock = threading.Lock()
    
    def worker(url: str) -> None:
        response = requests.get(url)
        with result_lock:
            results.append(response.text)
    
    threads = []
    for url in urls:
        thread = threading.Thread(target=worker, args=(url,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return results

# 2. Multiprocessing - Good for CPU-bound tasks
import multiprocessing

def cpu_intensive_task(data: List[int]) -> int:
    """CPU-intensive calculation."""
    return sum(x * x for x in data)

def process_with_multiprocessing(datasets: List[List[int]]) -> List[int]:
    """Process multiple datasets using multiprocessing."""
    with multiprocessing.Pool() as pool:
        results = pool.map(cpu_intensive_task, datasets)
    return results

# 3. Asyncio - Good for many concurrent I/O operations
import asyncio
import aiohttp

async def fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    """Fetch a single URL asynchronously."""
    async with session.get(url) as response:
        return await response.text()

async def fetch_all_urls(urls: List[str]) -> List[str]:
    """Fetch multiple URLs concurrently using asyncio."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# 4. Distributed Processing with Ray - Good for large-scale parallel computing
import ray

ray.init()

@ray.remote
def process_chunk(chunk: List[int]) -> int:
    """Process a chunk of data."""
    return sum(x * x for x in chunk)

def distributed_processing(data: List[int], chunks: int = 10) -> int:
    """Process data using distributed computing with Ray."""
    chunk_size = len(data) // chunks
    data_chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    
    # Schedule tasks across the Ray cluster
    results = ray.get([process_chunk.remote(chunk) for chunk in data_chunks])
    return sum(results)
```

### Data Processing with Specialized Libraries

```python
# Pandas for tabular data processing
import pandas as pd
import numpy as np

def pandas_processing_example(csv_path: str) -> pd.DataFrame:
    """Efficient data processing with pandas."""
    # Read CSV efficiently
    df = pd.read_csv(csv_path, usecols=['date', 'value'])  # Only load needed columns
    
    # Vectorized operations (much faster than loops)
    df['value_squared'] = df['value'] ** 2
    df['date'] = pd.to_datetime(df['date'])  # Convert to datetime
    
    # Group and aggregate
    monthly_avg = df.groupby(pd.Grouper(key='date', freq='M')).agg({
        'value': 'mean',
        'value_squared': 'sum'
    })
    
    return monthly_avg

# Numpy for numerical processing
def numpy_calculation(data: List[float]) -> float:
    """Efficient numerical calculation with numpy."""
    # Convert to numpy array once
    arr = np.array(data)
    
    # Vectorized operations
    result = np.sum(np.sqrt(arr) * np.log(arr + 1))
    
    return float(result)

# Using dask for larger-than-memory datasets
import dask.dataframe as dd

def process_large_dataset(file_pattern: str) -> pd.DataFrame:
    """Process a dataset too large to fit in memory."""
    # Create dask dataframe from multiple files
    ddf = dd.read_csv(file_pattern)
    
    # Perform operations (these are lazy)
    result = ddf.groupby('category').agg({
        'value': ['mean', 'sum', 'count']
    })
    
    # Compute final result (triggers actual computation)
    return result.compute()
```

### Performance Examples

```python
from functools import lru_cache
import time
import cProfile
import pstats
from typing import Generator, TypeVar, Callable, Any

T = TypeVar('T')

def read_large_file(file_path: str) -> Generator[str, None, None]:
    with open(file_path, 'r') as f:
        for line in f:  # Reads one line at a time
            yield line.strip()

# ✅ GOOD: Caching expensive computations
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """Calculate fibonacci number with caching for performance."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Profiling example
def profile_function(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Profile a function's performance."""
    # Basic timing
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds")
    
    # Detailed profiling
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run multiple times for more accurate profiling
    for _ in range(5):
        func(*args, **kwargs)
    
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats(10)  # Print top 10 time-consuming functions
    
    return result

# Example usage
result = profile_function(fibonacci, 35)
```

## 12. Recommended Development Tools

- **Formatting**: Black (uncompromising code formatter)
- **Linting**: flake8 with plugins (mccabe, bugbear)
- **Import Sorting**: isort (automatically organize imports)
- **Type Checking**: mypy (static type checking)
- **Testing**: pytest with coverage.py
- **Dependency Management**: poetry or pipenv
- **Documentation**: Sphinx + readthedocs theme
- **Security Scanning**: bandit (static security analyzer)
- **Dead Code Detection**: vulture (finds unused code)
- **All-in-One Linter**: Ruff (fast Python linter)

### Configuration Examples

#### flake8 config (setup.cfg)
```ini
[flake8]
max-line-length = 88
exclude = .git,__pycache__,build,dist
ignore = E203, W503
```

#### isort config (.isort.cfg)
```ini
[settings]
profile = black
line_length = 88
multi_line_output = 3
```

#### mypy config (mypy.ini)
```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
```

#### pytest config (pytest.ini)
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

#### bandit config (.bandit)
```yaml
# Bandit configuration
skips: ['B101']  # Skip assert statements warning
exclude_dirs: ['tests', 'venv', '.venv']
```

#### Ruff config (ruff.toml)
```toml
line-length = 88
target-version = "py310"
select = ["E", "F", "I", "N", "UP", "ANN"]
ignore = ["ANN101"]  # Skip 'missing-type-self'
```

#### pre-commit config (.pre-commit-config.yaml)
```yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
    -   id: check-ast  # Verify syntax is valid
    -   id: detect-private-key  # Prevent accidental secret commits
-   repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
    -   id: black
-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort
-   repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: 'v0.0.254'
    hooks:
    -   id: ruff
        args: [--fix, --exit-non-zero-on-fix]
-   repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
    -   id: bandit
        args: ['-c', '.bandit']
```

## 13. CI/CD Best Practices

- Automate testing, linting, and deployment
- Use feature branches and pull requests
- Configure branch protection rules
- Implement staged deployments (dev → staging → production)
- Include security scanning in the pipeline
- Cache dependencies to speed up builds
- Implement parallel testing for faster feedback

### GitHub Actions Example

```yaml
name: Python CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      - name: Lint with Ruff
        run: ruff check .
      - name: Check formatting with Black
        run: black --check .
      - name: Type check with mypy
        run: mypy src
      - name: Security scan with Bandit
        run: bandit -r src -c .bandit

  test:
    needs: lint
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      - name: Test with pytest
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  deploy:
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Build package
        run: |
          pip install build
          python -m build
      - name: Deploy to staging
        run: |
          # Deployment commands here
          echo "Deploying to staging environment"
```