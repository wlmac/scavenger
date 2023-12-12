# Scavenger Hunt Website

A scavenger hunt website designed to prevent any form of cheating and RNG-based wins on a typical scavenger hunt. It was created in Django and uses OAuth 2.0 / OIDC-ish with the main [Metropolis](https://maclyonsden.com) site to handle authentication.

![image](https://github.com/wlmac/scavenger/assets/45807097/194b5ad8-d2f9-49a9-951f-5dd6d3ab51c3)

 
## credits
### project manager
Patrick Lin
### programming
nyiyui, Jason Cameron, Jimmy Liu, Glen Lin, Joshua Wang, Chelsea Wong
### content
Misheel Batkhuu
### UI/UX design 
Chelsea Wong

# setup

do normal django setup
then run 
```bash
python manage.py init
```

## Before you start a new hunt
```bash
python manage.py new_event
```
if you want to retain the old teams, import the old teams into the new event


