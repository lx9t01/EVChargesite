# EVChargesite
This site is designed for EV Charge facility's interface with backend database

The interface consists of 3 functional pages, namely index, EVCharge and Charging

index: 
  index is the main page and homepage.
  When Electrical Vehicle is connected to the charging facility, the car ID information 
    should be automatically read by the charging port, or can be manually input from 
    the textarea, which is efficient for the development phase. 
  The car ID usually can be plate number, and it should be registered in the database in
    advance to provide other information regarding the car, such as make, model, mile per
    kWh, a profile image, and so on. 
    
EVCharge: 
  EVCharge is the page shown after verifing the car information.
  After connected with the port, the driver should provide valid personal informaion such
    as Caltech ID number or credit card number (for the payment of charging battery)
  The additional information should also be provided:
    current timestamp as the beginning point of charging battery;
    expected duration of stay at the facility;
    expected length of travel after leaving the facility;
    and so on.
  Based on the information provided, we can pass the four cirtical parameters to the 
    optimization algorithm in the next step. (si, ti, ei, ri).
  si: start time of charge;
  ti: the predicted end time of charge;
  ei: the energy needed for the EV's next trip, calculated from expected travel distance;
  ri: average (or maximum) charging rate, determined by the car model
  
Charging: 
  Charging is the site where we set all the parameters and the charge begins.
  When we want to drive out the EV, a disconnect signal should be sent to our server, and this
    charging period ends. The data of today should be uploaded to our server as well, 

Other supporting systems: 
  Machine learning algorithm to train on history data;
  rRegistration page for new EVs.
