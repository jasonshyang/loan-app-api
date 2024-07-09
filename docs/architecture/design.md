# Tech design notes

## Endpoints
### user/create/
- POST: to create new user

### user/token/
- POST: to create new token

### user/profile/
- GET: to view profile
- PUT/PATCH: to update profile

### (to be implemented) account/
- GET: view details of a given account
- POST: to create a new account
- PUT/PATCH: update an account

### moneyrequest/
- GET: list all moneyrequests by the borrower
- POST: create a new moneyrequest

### (to be implemented) moneyrequest/all/
- GET: list all moneyrequests that are open

### moneyrequest/<moneyrequest_id>/
- GET: view details of a given moneyrequest
- PUT/PATCH: update a moneyrequest by the borrower
- DELETE: delete a moneyrequest

### (to be implemented) contract/
- GET: list all contracts associated with the user

## Data Model
### User
- email
- password
- name

### MoneyRequest
- title
- description
- amount
- frequency
- term
- (to be implemented) status

### (to be implemented) Account
- (FK) user
- balance: positive for asset, negative for debt
- risk_level: borrower specific
- risk_appetite: lender specific
- income: borrower specific

### (to be implemented) Contract - after a money request is accepted, a contract will be established between borrower and lender
- (FK) Money Request
- amount
- frequency
- term
- payment
- due_date
- status

## Celery tasks for scheduled operations
(to be implemented)

### Contract creation
- when a MoneyRequest is 'Agreed', auto create a Contract

### Payment transfer
- Payment processing on due date

### Aging
- Missed payment aging

### Contract closure
- When a contract has been fully paid, update the contract to 'Closed'