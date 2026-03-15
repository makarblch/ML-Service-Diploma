class MlServiceError(Exception):
    """Base exception for ML service."""


class FeatureValidationError(MlServiceError):
    """Raised when incoming features are invalid."""


class ModelNotFoundError(MlServiceError):
    """Raised when requested model or active model is not found."""


class JobNotFoundError(MlServiceError):
    """Raised when job status cannot be found."""