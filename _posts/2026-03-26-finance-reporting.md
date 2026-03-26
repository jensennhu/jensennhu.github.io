---
layout: post
title: Tracking Finances with Plaid, GoogleSheets, and R 
---

![networth_obfs](/images/networth_obfs.jpg)

![paycheck_overlay](/images/paycheck_overlay.jpg)

![test](/images/test.jpg)

**Aim**: Improve awareness of expenses and flow of money.  

**Introduction**: 
Knowing where your money goes is important. Did I spend beyond my budget on groceries this month? Am I spending more than 50% of my income on rent? Is lifestyle creep affecting my savings? When will I pay off my loans at my current savings rate? The only way to confidently answer these questions is by tracking your finances. Several years ago I used a free app called Mint that let you link your bank accounts and credit cards, etc. , it provided analytics, trends, and allowed me to refresh my balance and see all my transactions in one area. I loved using Mint, but alas, all good things come to an end and Mint shutdown. With that, I decided to build my own financial tracking tool.

**Methods:**
- Plaid for transactions and account balance data. Required a production level approval and three-step authentication.
- Google app script + google sheet for data pipeline/backend. I used an existing google app script [https://github.com/williamlmao/plaid-to-gsheets?tab=readme-ov-file]. There were a few updates I made to get the script to be functional, but generally, it required the access_tokens acquired from the earlier plaid three-step auth. I set the trigger in the app script to run every morning. 
- Main R scripts :
  - 01a_data_prep_live.R - reading in googlesheet data, cleaning, data construction
  - 02a_data_analytics.Rmd - main visualizations and summary html output to be hosted
  - 03a_md_accounts.Rmd - separate output for email notification
- Github actions for automation and orchestration.
- Cloudflare for hosting.  


**Lessons Learned**:
- This was my first time working with a 3-legged auth api. The process of gathering and storing access_tokens for each of my accounts could probably be improved by integrating an auth page into my application frontend instead of manual one-off auth and copy-pasting access_tokens into my google app script.
- The Google app script + google sheet as the backend works fine. A later improvement for better security and flow can be migrating this to a sql database.
- Plaid's categorization of expenses isn't perfect so mapping categories to correct labels requires continued iteration. The current case_when code structure to clean expense categories (shown below) is unwieldy and lacks as a robust long term solution. Listing these categories/rules into a separate googlesheet tab or local csv to serve as a look-up may be a more transparent and easily editable solution.   

>    `main_category = case_when(
      plaid_category_1 == "Shops"          & plaid_category_2 == "Supermarkets and Groceries"                      ~ "Groceries",
      plaid_category_1 == "Shops"          & plaid_category_2 == "Warehouses and Wholesale Stores"                 ~ "Costco",
      plaid_category_1 == "Shops"          & plaid_category_2 == "Food and Beverage Store"                         ~ "Dining out",
      plaid_category_1 == "Food and Drink" & (plaid_category_3 != "Coffee Shop" | is.na(plaid_category_3))         ~ "Dining out",
      plaid_category_3 == "Coffee Shop"                                                                            ~ "Coffee"...`

Disclaimer: the opinions expressed and analyses performed are solely my own and do not necessarily reflect the official policy or position of my employer.
