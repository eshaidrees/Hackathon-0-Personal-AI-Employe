# 🔧 Odoo Community Edition Setup Guide

**For AI Employee Gold Tier Integration**

---

## 📋 Overview

This guide walks you through setting up Odoo Community Edition for integration with your AI Employee system via the Odoo MCP Server (`scripts/odoo_mcp_server.py`).

---

## 🎯 Option 1: Quick Setup with Docker (Recommended)

### Step 1: Install Docker

**Windows:**
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Install and restart your computer
3. Open Docker Desktop to start the Docker service

**Mac:**
1. Download Docker Desktop from the same link
2. Drag to Applications folder
3. Open Docker Desktop

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### Step 2: Run Odoo with Docker

```bash
# Create a directory for Odoo data
mkdir odoo-data
cd odoo-data

# Run Odoo Community Edition
docker run -p 8069:8069 --name odoo -e ODOO_DATABASE=postgres -e ODOO_DB_USER=odoo -e ODOO_DB_PASSWORD=odoo -e ODOO_ADMIN_PASSWORD=admin -v odoo-data:/var/lib/odoo -d odoo:19.0
```

### Step 3: Access Odoo

Open your browser and go to: **http://localhost:8069**

### Step 4: Create Database

1. You'll see the Odoo database creation screen
2. Fill in:
   - **Database Name:** `odoo`
   - **Email:** your-email@example.com
   - **Password:** `admin` (or your choice)
3. Click **Create Database**

### Step 5: Install Accounting Module

1. After login, go to **Apps** menu
2. Search for "Accounting"
3. Click **Install** on "Invoicing" (free) or "Accounting" (full)
4. Wait for installation to complete

---

## 🖥️ Option 2: Manual Installation (Windows)

### Step 1: Download Odoo

1. Go to: https://www.odoo.com/page/download
2. Download **Odoo 19 Community Edition** for Windows
3. Run the installer

### Step 2: Install PostgreSQL

Odoo requires PostgreSQL database:

1. Download PostgreSQL: https://www.postgresql.org/download/windows/
2. Install PostgreSQL 15 or higher
3. Remember the password you set for `postgres` user

### Step 3: Configure Odoo

1. Run Odoo installer
2. Choose installation directory
3. When prompted for database:
   - Select **Use existing PostgreSQL**
   - Enter PostgreSQL password
4. Complete installation

### Step 4: Start Odoo Service

1. Odoo should start automatically
2. If not, run: `C:\Program Files\Odoo 19.0\server\odoo-bin.exe`
3. Access at: **http://localhost:8069**

---

## 🔑 Configure Environment Variables

Add these to your `.env` file in the AI Employee project:

```bash
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DATABASE=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

# Optional: For production
ODOO_API_KEY=your-api-key-if-using-api-authentication
```

---

## ✅ Test Odoo Connection

### Test 1: Basic Connection

```bash
cd C:\Users\PC\Desktop\Hackathon-0-AI-Employe\Personal-AI-Employe

# Activate virtual environment
venv\Scripts\activate

# Test Odoo MCP
python scripts/odoo_mcp_server.py demo
```

**Expected Output:**
```
Odoo MCP Demo Mode
Dry Run: true

1. Testing authentication...
✓ Authentication successful

2. Testing partner search...
Found partners: [{'id': 1, 'name': 'Demo Partner', 'email': 'demo@example.com'}]

3. Testing account summary...
Account Summary: {...}
```

### Test 2: Authentication (Live Mode)

```bash
# First, set DRY_RUN=false in .env
# Then test authentication
python scripts/odoo_mcp_server.py auth --url http://localhost:8069 --db odoo --user admin --password admin
```

---

## 📊 Create Sample Data in Odoo

### Create a Customer

1. Login to Odoo at http://localhost:8069
2. Go to **Contacts** → **Create**
3. Fill in:
   - **Name:** Test Customer
   - **Email:** customer@example.com
   - **Phone:** +1234567890
   - **Type:** Individual
4. Click **Save**
5. Note the **Contact ID** (shown in URL, e.g., `/web#id=1`)

### Create a Product

1. Go to **Invoicing** → **Products** → **Create**
2. Fill in:
   - **Product Name:** Consulting Service
   - **Product Type:** Service
   - **Sales Price:** $150
3. Click **Save**
4. Note the **Product ID**

### Create an Invoice

1. Go to **Invoicing** → **Customers** → **Create**
2. Select the customer you created
3. Add invoice lines:
   - **Product:** Consulting Service
   - **Quantity:** 10
   - **Price:** $150
4. Click **Save**
5. Click **Post** to confirm

---

## 🔗 Test AI Employee Integration

### Test 1: Search for Partner

```bash
python scripts/odoo_mcp_server.py search_partner --url http://localhost:8069 --db odoo --user admin --password admin
```

### Test 2: Get Invoices

```bash
python scripts/odoo_mcp_server.py get_invoices --url http://localhost:8069 --db odoo --user admin --password admin
```

### Test 3: Get Account Summary

```bash
python scripts/odoo_mcp_server.py summary --url http://localhost:8069 --db odoo --user admin --password admin
```

### Test 4: Create Invoice (with approval workflow)

```bash
# This will create an approval request in Pending_Approval folder
python scripts/odoo_mcp_server.py create_invoice --partner-id 1 --amount 1500 --vault ../AI_Employee_Vault
```

---

## 🛠️ Troubleshooting

### Error: "Connection refused"

**Solution:**
1. Check if Odoo is running: Open http://localhost:8069
2. Check Docker container: `docker ps | grep odoo`
3. Restart Odoo: `docker restart odoo`

### Error: "Authentication failed"

**Solution:**
1. Verify credentials in `.env` file
2. Try logging in manually at http://localhost:8069
3. Reset admin password in Odoo if needed

### Error: "Database not found"

**Solution:**
1. Check database name in `.env` matches your Odoo database
2. Create database at: http://localhost:8069/web/database/manager

### Error: "Module not found"

**Solution:**
1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure `requests` library is installed:
   ```bash
   pip install requests
   ```

---

## 📝 Odoo MCP Server Usage Examples

### Search for Customer by Email

```bash
python scripts/odoo_mcp_server.py search_partner \
  --url http://localhost:8069 \
  --db odoo \
  --user admin \
  --password admin
```

### Create New Customer

```bash
python scripts/odoo_mcp_server.py create_partner \
  --url http://localhost:8069 \
  --db odoo \
  --user admin \
  --password admin
```

**Note:** You'll need to modify the script to accept command-line arguments for partner creation. Here's a quick example:

```python
# Add to odoo_mcp_server.py main() function
elif args.action == 'create_partner':
    result = mcp.create_partner(
        name='New Customer',
        email='customer@example.com',
        phone='+1234567890'
    )
    print(f'Result: {result}')
```

### Post Invoice

```bash
python scripts/odoo_mcp_server.py post_invoice \
  --url http://localhost:8069 \
  --db odoo \
  --user admin \
  --password admin \
  --invoice-id 1
```

### Register Payment

```bash
python scripts/odoo_mcp_server.py register_payment \
  --url http://localhost:8069 \
  --db odoo \
  --user admin \
  --password admin \
  --invoice-id 1 \
  --amount 1500
```

---

## 🔄 AI Employee + Odoo Workflow

### Complete Invoice Flow

```
1. Email received: "Please send invoice"
   ↓
2. Gmail Watcher → Creates Needs_Action/EMAIL_*.md
   ↓
3. Orchestrator → Triggers Claude Code reasoning
   ↓
4. Odoo MCP → Searches for customer in Odoo
   ↓
5. Odoo MCP → Creates invoice in Odoo (draft)
   ↓
6. Creates approval: Pending_Approval/ODOO_APPROVAL_*.md
   ↓
7. Human reviews → Moves to Approved/
   ↓
8. Odoo MCP → Posts invoice in Odoo
   ↓
9. Email MCP → Sends invoice via Gmail
   ↓
10. Task moved to Done/
   ↓
11. Weekly Audit → Includes in CEO Briefing
```

---

## 🔐 Security Best Practices

1. **Never use admin credentials in production**
   - Create dedicated API user with limited permissions

2. **Use API Keys instead of passwords**
   - Go to: Settings → Users → API Keys
   - Generate new API key for AI Employee

3. **Enable HTTPS for production**
   - Use reverse proxy (nginx) with SSL certificate
   - Or use Odoo.sh for managed hosting

4. **Restrict database access**
   - Only allow connections from localhost
   - Use firewall rules for remote access

---

## 📚 Additional Resources

- **Odoo Documentation:** https://www.odoo.com/documentation/19.0/
- **Odoo JSON-RPC API:** https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
- **Docker Odoo:** https://hub.docker.com/_/odoo
- **Odoo Community:** https://www.odoo.com/forum/community-1

---

## 🎯 Next Steps

After setting up Odoo:

1. ✅ Test basic connection with `odoo_mcp_server.py demo`
2. ✅ Create sample customers and invoices
3. ✅ Test AI Employee integration workflows
4. ✅ Configure approval thresholds in Company_Handbook.md
5. ✅ Run weekly audit to see Odoo data in CEO Briefing

---

*Odoo Setup Guide - AI Employee Gold Tier*
*Last Updated: 2026-03-14*
