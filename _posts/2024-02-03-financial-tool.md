---
layout: post
title: Tracking Finances with Plaid, GoogleSheets, and R 
---

![mh_needs_svi_dash2](/images/mh_needs_svi_dash.PNG)  

Aim: Improve awareness of expenses and overall flow of money.
Introduction: Knowing where your money goes is important. Did I spend beyond my budget on groceries this month? Am I spending more than 50% of my income on rent? Is lifestyle creep affecting my savings? When will I pay off my loans at my current savings rate? The only way to confidently answer these questions is by tracking your finances. Several years ago I used a free app called Mint that let you link your bank accounts and credit cards, etc. , it provided analytics, trends, and allowed me to refresh my balance and see all my transactions in one area. I loved using Mint, but alas, all good things come to an end and Mint shutdown. With that, I decided to build my own financial tracking tool!

Methods:
To get transaction and account balance data, I used Plaid. After signing up and being granted production level access, I was able to connect my accounts using their api which has three-steps to authentication: 1) generate a link_token on your server to initialize Plaid Link, 2) authenticate with bank of interest via the Link widget to produce a public_token, and 3) exchange the public_token for an access_token to securely fetch financial data. Thankfully plaid has a quick start guide to help with this process. 

To support backend data pipeline, processing of the Plaid data, I used an existing google app script here[https://github.com/williamlmao/plaid-to-gsheets?tab=readme-ov-file]. There were a few updates, I made to get the script to be functional, but generally, it required the access_tokens you get from the earlier plaid three-step auth. 

To read the processed data, I used the R library googledrive to import for the GoogleSheet. 

- Credit vs debit 
- Income vs expenses
- Cleaning the data
- Creating categorizes (if-then statements) 

Rmarkdown for visual plotting and tabular info. Render as html to then be hosted. 



Image capture to show as PNG for email

For more details on steps, I have a list on notion: https://www.notion.so/198eded585c04c8b98700e699edfc673?v=80a8cc6d457a41d6a0bd848b6f833a95&source=copy_link  

- Plaid for transactions and account balance data
- Google app script + google sheet for data pipeline/backend 
- R scripts for data cleaning, construct development, and reporting
- Github actions for automation and orchestration
- Cloudflare for hosting

Lessons Learned
- 

Data Sources:


Find out more by exploring my [dashboard](https://jensennhu.github.io/covid19_mh_need/) (best opened on desktop)  
Also, [visit the project on GitHub](https://github.com/jensennhu/covid19_mh_need).  

Disclaimer: the opinions expressed and analyses performed are solely my own and do not necessarily reflect the official policy or position of my employer.
