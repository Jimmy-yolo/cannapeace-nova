# Restaurant LINE-to-Excel Order Bridge (D2)

**DEMO READY** | 2-Day Timebox | Setup: 3-5K THB | Subscription: 499-999 THB/mo

## Problem

Thai restaurants receive 20-50 orders daily via LINE (customer messages + photos).
Staff manually re-type each order into Excel/Google Sheets for kitchen and accounting.
**Time waste:** 2-4 hours/day per restaurant.

## Solution (Demo)

LINE bot that:
1. Receives 8-10 sample order messages (Thai/Chinese/English mixed)
2. Parses: customer name, items, quantities, total
3. Appends to Google Sheet automatically
4. Sends daily summary message to owner

## Happy Path Only

- Sample data: 10 pre-written order messages
- No photo OCR (text messages only for demo)
- No inventory tracking
- No payment integration
- No multi-restaurant support
- Single Google Sheet output

## Tech Stack

- LINE Messaging API (webhook)
- FastAPI (webhook receiver)
- OpenAI GPT-4 (order parsing)
- Google Sheets API (append rows)
- Sample Thai/Chinese/English order formats

## Day 1 (Today)

- [ ] LINE bot webhook scaffold
- [ ] 10 sample order messages
- [ ] Order parser (GPT-4)
- [ ] Google Sheets appender
- [ ] Local testing with ngrok

## Day 2 (Tomorrow)

- [ ] Daily summary message
- [ ] Deploy to Railway
- [ ] Pitch script
- [ ] Demo video (30 sec)

## Pricing

- Pay-per-order: 5-10 THB/order
- Monthly unlimited: 499-999 THB/mo
- Setup fee: 3,000-5,000 THB one-time
