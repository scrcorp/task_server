# PDCA Plan: Notification Channel (Extensible Delivery)

> **Feature**: notification-channel
> **Created**: 2026-02-13
> **Status**: Plan
> **Priority**: High

---

## 1. Background & Objective

Currently, comments and feedback create notification records in the `notifications` table, but these are only visible via the in-app API (`GET /notifications`). Users must open the app to see them.

The goal is to add an extensible notification delivery system that:
- Sends email notifications when comments/feedback are created
- Uses a Strategy Pattern so new channels (SMS, push, etc.) can be added easily
- Keeps the existing in-app notification unchanged

---

## 2. AS-IS vs TO-BE

### AS-IS

```
Comment/Feedback Created
    ↓
NotificationRepository.create() → DB record only
    ↓
User must check in-app to see notification
```

- No external delivery (email, SMS, push)
- NotificationService only reads/marks notifications
- CommentService creates comments without triggering notifications
- No notification dispatch logic exists

### TO-BE

```
Comment/Feedback Created
    ↓
NotificationService.notify() → DB record + dispatch
    ↓
NotificationDispatcher (Strategy Pattern)
    ├── InAppChannel (default, DB only — already exists)
    ├── EmailChannel (SMTP via existing email.py)
    ├── (Future) SMSChannel
    └── (Future) PushChannel
```

---

## 3. Architecture: Strategy Pattern

```
INotificationChannel (ABC)
├── send(recipient_email, title, message, context) → bool
│
├── EmailNotificationChannel
│   └── Uses app/core/email.py send_email()
│   └── Loads notification_email.html template
│
├── (Future) SMSNotificationChannel
│   └── Uses Twilio/other SMS API
│
└── (Future) PushNotificationChannel
    └── Uses FCM/APNs
```

```
NotificationDispatcher
├── channels: List[INotificationChannel]
├── dispatch(recipient, title, message, context) → None
│   └── for channel in channels: channel.send(...)
└── Registered channels configurable via DI
```

---

## 4. Requirements

### 4.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Create `INotificationChannel` interface with `send()` method | Must |
| FR-02 | Create `EmailNotificationChannel` using existing email.py | Must |
| FR-03 | Create `NotificationDispatcher` that dispatches to registered channels | Must |
| FR-04 | Create `notification_email.html` template for notification emails | Must |
| FR-05 | Add `notify()` method to `NotificationService` that creates DB record + dispatches | Must |
| FR-06 | Trigger notification when comment is created | Must |
| FR-07 | Trigger notification when feedback is created | Must |
| FR-08 | Include notification type in `NotificationType` enum: `comment` | Should |
| FR-09 | Look up recipient email from `user_profiles` via `IAuthRepository` | Must |
| FR-10 | Handle email send failures gracefully (log, don't block main flow) | Must |

### 4.2 Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | Adding a new channel requires only: 1) implement INotificationChannel, 2) register in DI |
| NFR-02 | Email failures must not break comment/feedback creation |
| NFR-03 | No new dependencies required |
| NFR-04 | Unit tests with pytest |

---

## 5. Scope

### In Scope

- `INotificationChannel` interface
- `EmailNotificationChannel` implementation
- `NotificationDispatcher` class
- `NotificationService.notify()` method
- Integration with `CommentService` and feedback creation
- HTML email template for notifications
- Unit tests

### Out of Scope

- SMS channel (future)
- Push notification channel (future)
- User notification preferences (enable/disable per channel)
- Notification batching/digest
- Admin UI for notification settings

---

## 6. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `app/notifications/__init__.py` | Create | Package init |
| `app/notifications/channel.py` | Create | INotificationChannel interface + EmailNotificationChannel |
| `app/notifications/dispatcher.py` | Create | NotificationDispatcher class |
| `app/templates/notification_email.html` | Create | Email template for notifications |
| `app/models/enums.py` | Modify | Add `COMMENT = "comment"` to NotificationType |
| `app/services/notification_service.py` | Modify | Add `notify()` method with dispatcher |
| `app/services/comment_service.py` | Modify | Trigger notification on comment create |
| `app/core/dependencies.py` | Modify | Wire dispatcher and updated services |
| `tests/test_notification_channel.py` | Create | Unit tests for channel & dispatcher |
| `tests/test_notification_integration.py` | Create | Integration tests for comment → notification flow |

---

## 7. Implementation Order

| Step | Task | Dependencies |
|------|------|-------------|
| 1 | Create `INotificationChannel` interface | None |
| 2 | Create `EmailNotificationChannel` | Step 1 |
| 3 | Create `notification_email.html` template | None |
| 4 | Create `NotificationDispatcher` | Step 1 |
| 5 | Add `COMMENT` to `NotificationType` enum | None |
| 6 | Add `notify()` to `NotificationService` | Step 4 |
| 7 | Update `CommentService` to trigger notification | Step 6 |
| 8 | Update feedback creation to trigger notification | Step 6 |
| 9 | Update DI container | Step 7, 8 |
| 10 | Write unit tests | Step 9 |
| 11 | Update API spec documentation | Step 10 |

---

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| SMTP failure blocks comment creation | High | Wrap email send in try/except, log error, don't re-raise |
| Slow email sending blocks API response | Medium | Email sending is fast via SMTP; can add async background task later if needed |
| Missing recipient email | Low | Skip notification for users without email |

---

## 9. Acceptance Criteria

- [ ] INotificationChannel interface with `send()` method exists
- [ ] EmailNotificationChannel sends emails via existing SMTP
- [ ] NotificationDispatcher dispatches to all registered channels
- [ ] Comment creation triggers in-app + email notification to assignment owner
- [ ] Feedback creation triggers in-app + email notification to target user
- [ ] Email failures are caught and logged, not re-raised
- [ ] Adding a new channel only requires implementing interface + DI registration
- [ ] All unit tests pass
