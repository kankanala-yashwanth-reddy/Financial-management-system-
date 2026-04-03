# GitHub Setup Instructions

## Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Fill in the form:
   - **Repository name:** `financial-management-system`
   - **Description:** Financial management platform with 3-page quiz
   - **Public** (selected)
   - **Do NOT** initialize with README, .gitignore, or license (we already have them)
3. Click **Create repository**

## Step 2: Push Code to GitHub

After creating the repo, you'll see a page with commands. Run these commands in PowerShell:

```powershell
cd "d:\Financial Management System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/financial-management-system.git
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username!**

You may be prompted for authentication - either:
- Enter your GitHub username and personal access token, OR
- Use GitHub CLI if you have it installed

## Step 3: Verify

- Go to https://github.com/YOUR_USERNAME/financial-management-system
- You should see all your files uploaded!

## Next Step

Once pushed, reply and I'll help you deploy to Render.com for a permanent backend URL.
