---
layout: post
title: Spike Detection
date: 2026-03-28
---

**Aim**:  
(1) Learn about computer vision in volleyball.
(2) Use AI to create an end-to-end platform to assist with training a computer vision model to detect spikes and classify phases. 
(3) Leveraging the trained model, use AI to create a mobile app to save users spike videos and record bio-mechanic metrics. 
  
**Introduction**:
Volleyball is one of my favorite activities. Over the past few years, I've gotten more invested into improving my technique and  game play. Watching youtube videos on how to pass better, professional player highlights in slow-mo, participating in tournaments, attending clinics... the grind to get better is lifelong journey. 

One skill I've gotten better at is hitting (spiking). Although it can be simplified to just "jumping and smacking the ball" there's a breadth of nuance and serious biomechanics behind it. From the approach and intentional shift in momentum, to torque derived from the connection of the hip and shoulder separation, there is ton to analyze. I often record my own hits to pick at specific details. Constant pausing and unpausing to segment and decipher body positioning in relation to the ball, reviewing what I could do better next time. As someone looking for ways to improve, I thought computer vision and volleyball was a natural choice.

**DRAFT IN PROGRESS**:
*Current Research*:
Fast ball tracking
Court vision and boundary segmentation
Skeletal data 
Person tracking
Action-based categorization using LSTM

Initial Pipeline:
Harvest youtube videos -> import into CVAT and annotate -> export as COCO format -> run python script to map skeletal data to annotated frames -> run python script to stack data and train/test split -> evaluate model 


Desired uses:
Detecting people and the ball.
Detecting hits (spikes). 
Classification of a spike sequence.
Biomechanic metrics.
 
Lessons Learned:
- Think about project processes and use AI to create your own SAAS to improve project efficiency and scalability early on. This sounds like overkill, but making progress on a long term project can be tough and often requires regrouping, reorganizing, re-everything. Your process may be straightforward on day one, but each new script or project branch or third party tool can increase process complexity and stretch your attention and resources (especially if outside SAAS aren't free). For example, when training the LSTM model, I initially uploaded a video to CVAT (platform for annotating videos), label the sequences, output and archive my annotations, import them into a python script to map those annotations to skeletal data based on their frame reference numbers, stack on existing data, run another python script to train/test split, evaluate the model. Doing this one or two times is fine, but knowing I might need to do this hundreds of times, became a growing concern. So I prompted claude to create an end-to-end platform that would integrate the capabilities of CVAT and my python scripts, designed specifically to import, collect, label, amass a dataset of videos, and track the training/evaluation of my models.
 

Disclaimer: the opinions expressed and analyses performed are solely my own and do not necessarily reflect the official policy or position of my employer.

![spike_portfolio_1](/images/spike_portfolio_1.png)
