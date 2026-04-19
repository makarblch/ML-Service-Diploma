from enum import Enum


class JobStatus(str, Enum):
    # accepted = "accepted"
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class CompanySize(str, Enum):
    se = "SE"
    me = "ME"
    le = "LE"


class JobEventType(str, Enum):
    job_received = "job_received"
    preprocessing_started = "preprocessing_started"
    preprocessing_completed = "preprocessing_completed"
    model_lookup_started = "model_lookup_started"
    model_loaded = "model_loaded"
    inference_started = "inference_started"
    inference_completed = "inference_completed"
    callback_started = "callback_started"
    callback_sent = "callback_sent"
    callback_failed = "callback_failed"
    job_failed = "job_failed"


class ErrorStage(str, Enum):
    request_validation = "request_validation"
    model_lookup = "model_lookup"
    artifact_loading = "artifact_loading"
    preprocessing = "preprocessing"
    inference = "inference"
    callback = "callback"
    internal = "internal"