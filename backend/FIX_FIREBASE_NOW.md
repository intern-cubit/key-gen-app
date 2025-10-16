# Firebase Service Account Key Replacement Guide

## ⚠️ YOUR CURRENT KEY IS INVALID!

The error `Invalid JWT Signature` means your firebase-service-account.json has invalid credentials.

## 🔄 Steps to Fix:

### 1. Download Fresh Key from Firebase Console

1. Go to: https://console.firebase.google.com/
2. Select your project: **keygen-c60ec**
3. Click the gear icon ⚙️ → **Project Settings**
4. Go to **Service Accounts** tab
5. Click **"Generate new private key"** button
6. Click **"Generate key"** to confirm
7. A `.json` file will be downloaded

### 2. Replace the Old Key File

```powershell
# Navigate to backend folder
cd "d:\Codes\CuBIT Internship\whatsapp_marketing\key-generation-app\backend"

# Backup the old file (optional)
Rename-Item firebase-service-account.json firebase-service-account.json.OLD

# Copy the newly downloaded file here and rename it to:
# firebase-service-account.json
```

### 3. Rebuild the Backend

```powershell
# Clean old build
.\cleanup_build.ps1

# Rebuild with PyInstaller
python -m PyInstaller fastapibackend.spec
```

### 4. Test It Works

```powershell
# Start the app
npm start

# Or test backend directly
cd backend
python run_server.py

# You should see:
# ✅ FIREBASE CONNECTED SUCCESSFULLY!
# (No more JWT Signature errors)
```

---

## 📅 How Often to Update?

**NEVER! (unless...):**

✅ Keys don't expire automatically
✅ Once downloaded, they work forever

**You ONLY need to regenerate when:**

❌ Someone deletes the key in Firebase Console
❌ Key gets compromised (leaked publicly)
❌ You're rotating keys for security best practices (e.g., every 6-12 months)
❌ You switch Firebase projects

---

## 🔒 Security Reminder

**NEVER commit firebase-service-account.json to Git!**

✅ Already in your .gitignore
✅ But double-check it's not tracked:

```powershell
git ls-files | Select-String "firebase-service-account.json"
```

If it shows up, remove it:

```powershell
git rm --cached backend/firebase-service-account.json
git commit -m "Remove Firebase credentials from Git"
```

---

## 🎯 Summary

| Question | Answer |
|----------|--------|
| Do I download it every day? | **NO!** Once is enough |
| When do I need a new one? | Only if deleted, compromised, or rotated |
| How long is it valid? | **Forever** (until manually revoked) |
| Is my current one working? | **NO!** You need to download a fresh one |

---

After replacing the file, your errors will disappear! 🎉
