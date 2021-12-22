console.log('test 3');

let overlayContent = `
   <div class="popup-content">
      <div class="close-button">
         <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 310.3 310.37">
            <path d="M310.3,297.64c-2.08,6.06-5.62,10.65-12.19,12.24a15.32,15.32,0,0,1-13.65-3.07,37.48,37.48,0,0,1-3.32-3.11q-61.62-61.6-123.21-123.24a18.61,18.61,0,0,1-2-3l-1.45,0a18.66,18.66,0,0,1-2,3q-61.9,62-123.84,123.91c-4.6,4.61-9.78,7.07-16.36,5.48a15.88,15.88,0,0,1-8.52-25.68c1-1.16,2.07-2.21,3.14-3.28q61.4-61.41,122.81-122.78a20.69,20.69,0,0,1,3.25-2.22l0-1.47a21.3,21.3,0,0,1-3.23-2.24Q67.81,90.42,6.07,28.5A22.22,22.22,0,0,1,.63,19.68C-1.66,12,2.57,4.26,10,1.19,10.87.81,11.76.4,12.65,0h6.67c4.91,1.67,8.48,5.14,12.05,8.72Q91.94,69.41,152.6,130c.83.83,1.69,1.63,3,2.83,1-1.26,1.79-2.36,2.71-3.29q60.93-61,121.85-121.92c3.33-3.34,6.76-6.32,11.39-7.61h6.07A18.2,18.2,0,0,1,310.3,12.73V19.4c-1.6,4.72-4.87,8.19-8.31,11.63q-60.8,60.68-121.51,121.42a18.62,18.62,0,0,1-3,2v1.38a19.25,19.25,0,0,1,3,2q60.87,60.81,121.72,121.64c3.38,3.37,6.55,6.79,8.1,11.41Z"></path>
         </svg>
      </div>
        <div style="font-weight: bold">
        The purpose of this page is to compare data on Covid19 infections, vaccination rates, and 2021 voting results in Germany (by state).<br><br></div>
        
        <div>The charts for infections and vaccination coverage starts in June 2021, since this is the date at which vaccinations became available for everyone in Germany.
        Data on vaccination and infections are updated daily.<br><br>
        </div>
        <div style="font-weight: bold">What can you do?</div>
        <ul>
        <li><b>Zooming on the maps:</b> when you hold your mouse on the map, you’re able to zoom in/out by scrolling.</li>
        <li><b>Look-up:</b> By hovering over the data (charts or maps) you can see the exact data for the given state or party as well as point in time.</li>
        </ul>
        <div><b>Sources</b></div>
        <ul>
            <li>Vaccination data: <a href="https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html">The Robert Koch Institut (RKI)</a></li>
            <li>Covid-19 infection data: <a href="https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Daten/Impfquoten-Tab.html">The Robert Koch Institut (RKI)</a></li>
            <li>Voting data: <a href="https://www.bundeswahlleiter.de/">Bundeswahlleiter</a></li>
        </ul>
   </div>`;
let overlay = document.createElement('div');
overlay.classList.add('overlay');
overlay.innerHTML = overlayContent;
document.querySelector('body').appendChild(overlay);

overlay.querySelector('.close-button').addEventListener('click', ()=>{
    overlay.classList.remove('active');
})

let helpButton = document.createElement('div');
helpButton.classList.add('help');
helpButton.innerHTML="?";
helpButton.addEventListener('click', ()=>{overlay.classList.add('active')});
document.querySelector('body').appendChild(helpButton);

