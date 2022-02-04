---
layout: post
title: Automated email reporting during the COVID-19 Pandemic (July 2020 - Present)  
---  

**Aim:** Reduce anxiety, stress, and misinformation during the COVID-19 pandemic by providing consistent reporting in an easily digestible and accessible format. Take in feedback from end-users/consumers, identify areas of improvement. 

**Introduction**  
In New York City's first COVID-19 wave (starting April 2020), I was overwhelmed parsing through new information, news, and data being released about COVID-19. In April, New York Times released their public ongoing repository for COVID-19 data for researchers and officials. Dashboards and visualizations were built and released, but I didn't find them personable. Instead of a standing resource of high-level information to visit, I was looking for reliable data points on the outbreak to be delivered to me, daily. This is where automated email reporting came into play!

**Methods**   
There were three main R scripts to:
- (1) Load and transform COVID-19 data from NYTimes and JHU. 
- (2) Compile tables and plots into report layout using RMarkdown
- (3) Email compiled report to recipients using Blastula package  

This email report was sent to ~20+ people interested in receiving daily updates on COVID-19. Recipients were able to provide ongoing feedback to improve the report's interpretability and content. Edits were made to the main scripts in a staging folder separate from a production folder. I automated the report distribution using my computer's windows task scheduler which triggered a .bat file and subsequently the "send_email.R" script. Sending an email from R required an email account/provider that allowed third-party access.


<details>
  <Code>
    Code
  </Code>
  ```
  ``` 
# create metric views for domestic(state, county) and international 
state_fun <- function(place){
  (if (place %in% us_states){
      filter(covid_state, covid_state$state == {place})
      } else if (place %in% us_counties){
        filter(covid_county, covid_county$county == {place})
        } else if (place %in% province){
          filter(international, international$`Province/State` == {place})
        } else if (place %in% country){
          filter(international, international$`Country/Region` == {place}, international$`Province/State` == "")
        } else {
          place
        }) %>% 
    # row difference w/NA padding for x record(s) depending on look back
    mutate(cases_new = c(NA, diff(.$cases)),
           cases_new_week = c(rep(NA, 7), diff(.$cases, lag = 7)),
           cases_new_two_week = c(rep(NA, 14), diff(.$cases, lag = 14)),
           deaths_new = c(NA, diff(.$deaths)),
           deaths_new_week = c(rep(NA, 7), diff(.$deaths, lag = 7)),
           deaths_new_two_week = c(rep(NA, 14), diff(.$deaths, lag =  14)),
           # percent change in cases from yesterday
           cases_pct_growth = (cases/lag(cases) - 1) * 100,
           # 7 day moving average for new cases 
           cases_week_mavg = EMA(cases_new, n = 7),
           # percent change in 7 day moving average in new cases (from the previous week)
           cases_week_pct_mavg = (cases_week_mavg/lag(cases_week_mavg, n = 7) - 1) * 100,
           # percent change in 7 day moving average in new cases (from the previous day)
           cases_day_pct_mavg = (cases_week_mavg/lag(cases_week_mavg, n = 1) - 1) * 100,
           # Show sign
           sign = sign(cases_week_pct_mavg),
           # 7 day moving average for new deaths
           deaths_week_mavg = EMA(deaths_new, n = 7),
           # percent change in 7 day moving average in new deaths (from the previous week)
           deaths_week_pct_mavg = (deaths_week_mavg/lag(deaths_week_mavg, n = 7) - 1) * 100
           )
}
```
</details>

**Lessons Learned**  
Here are some of the major lessons learned from this project:  
- Delays and issues in uploading information to data sources happen. Set flags within scripts to terminate code when necessary. 
- In order to successfully automate a script, consider a cloud-based solution. My local desktop computer's window task scheduler depends on AC power and wifi/internet connection (the latter for pulling data from github and sending emails). If either of those pieces were missing, the report did not go out. 
- Blastula and mailR packages are great options for email distribution via R. I ended up going with Blastula because it was able to render an rmarkdown file which was easier to customize.

**Data Source:** https://github.com/nytimes/covid-19-data

Tools: blastula, dplyr, ggplot2

![mh_needs_svi_dash2](/images/joined1_2.jpg)
![mh_needs_svi_dash2](/images/joined3_4.jpg)


Also, [visit the project on GitHub](https://github.com/jensennhu/automated_sitrep_covid19).  

Disclaimer: the opinions expressed and analyses performed are solely my own and do not necessarily reflect the official policy or position of my employer.
