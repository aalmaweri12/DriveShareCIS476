# patterns/__init__.py
# Initialize the patterns package and make key classes available at the package level

# Singleton Pattern
from .singleton import UserSession

# Observer Pattern
from .observer import (
    NotificationObserver,
    EmailNotifier,
    AppNotifier,
    NotificationSubject,
    BookingManager
)

# Mediator Pattern
from .mediator import (
    UIMediator,
    BaseComponent,
    SearchComponent,
    BookingComponent,
    MessageComponent
)

# Builder Pattern
from .builder import (
    CarListingBuilder,
    CarListingDirector
)

# Proxy Pattern
from .proxy import (
    IPaymentProcessor,
    RealPaymentProcessor,
    PaymentProxy
)

# Chain of Responsibility Pattern
from .chain import (
    PasswordRecoveryHandler,
    QuestionOneHandler,
    QuestionTwoHandler,
    QuestionThreeHandler,
    PasswordResetHandler
)