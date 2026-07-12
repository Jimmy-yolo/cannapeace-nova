# Railway Google Sheets Setup

## Step 1: Access Railway Dashboard

Open: https://railway.app/project/dc08489d-44af-4c83-9777-bb02dc5bda75

Click on the **cannapeace-nova** service

## Step 2: Add Environment Variables

Click **Variables** tab, then add these two variables:

### Variable 1: GOOGLE_SHEET_ID

```
Name: GOOGLE_SHEET_ID
Value: 1Rz1DbllW-0ezJKM4Qsf58D8WAMPxuP5HOXzAbVgMQIY
```

### Variable 2: GOOGLE_CREDENTIALS_BASE64

```
Name: GOOGLE_CREDENTIALS_BASE64
Value: (see credentials_base64.txt - copy entire content)
```

The base64 value is saved in: `/Users/jimmy/repos/cannapeace-nova/demos/restaurant-line-to-excel/credentials_base64.txt`

## Step 3: Deploy

Railway will automatically redeploy after adding the variables.

Wait ~1 minute for deployment to complete.

## Step 4: Test

Send a test message to your LINE bot:

```
สวัสดีค่ะ ขอสั่ง:
- ไทยสติ๊ก 5 กรัม
- มังโก้คัช 3 กรัม
รวม 2,450 บาท
ชื่อ: คุณสมชาย
โทร: 081-234-5678
```

Check your Google Sheet - a new row should appear!

## Troubleshooting

If it doesn't work:
1. Check Railway logs: Click on **Deployments** → Latest deployment → **View Logs**
2. Look for errors mentioning "Google" or "Sheets"
3. Verify sheet is shared with: `cannapeace-line-bot@cannapeace-line-bot-502207.iam.gserviceaccount.com`

## Security Note

The base64 credentials file is gitignored and will NOT be committed.
Only reference exists in Railway environment variables (encrypted by Railway).
