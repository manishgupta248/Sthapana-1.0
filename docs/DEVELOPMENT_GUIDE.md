## Git
### Phase - 0
> git add .
> git status

> git commit -m "Phase 0: Foundation - Django skeleton, custom user model, auth pages, logging, backups, tests"
> git tag v0.0

> git add .
> git commit -m "docs: close out Phase 0 - update PROGRESS, CURRENT_STATUS, TODO, DECISIONS"

### Phase- 1 
# 
> git checkout -b phase-1-step-1-1-employee-foundation

> git status
> git add -A
> git commit -m "Step 1.1: Employee foundation (Department, Designation, Employee CRUD, audit trail, Excel import, dashboard count)"
### Phase 1.2 
> git checkout -b phase-1-step-1-2-contact-details

> git add -A
> git commit -m "Step 1.2: Contact Details (extension table, web form, Excel import)"

> git checkout main
> git merge phase-1-step-1-2-contact-details
> git branch -d phase-1-step-1-2-contact-details
> git add docs/
> git commit -m "Update docs: Step 1.2 complete, Steps 1.3-1.9 paused at owner's request"
> git checkout -b feature-lookup-excel-import

### Phase 7
> git checkout -b phase-7-telegram-integration

### Important commands
// check the exact versions installed (you'll need these for requirements/base.txt below):
> pip freeze | findstr /I "simple-history openpyxl"

##  Phase 0 with Step 0.1: Git repository + Python virtual environment setup.

# 1. Go to where you want the project folder (adjust drive/path if needed)
> cd D:\
> mkdir Sthapana
> cd Sthapana

# 3. Initialize Git tracking in this folder
> git init
> git status
# 4. Confirm Python is installed and check the version (we need 3.12)
> python --version

# 5. Create the virtual environment (creates a subfolder called "venv")
> python -m venv venv
> .\venv\Scripts\Activate.ps1