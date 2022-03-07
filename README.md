
<div align="center">
    <h1>Quivia: A Quiz Website</h1>
    <a href="#screenshots"><strong>View screenshots »</strong></a>
    <br/>
    <br />
    <p>A quiz website I started creating during the Covid-19 lockdown in 2020, to play Quizzes that I created, with my family.</p>
</div>

<details open="open">
<summary>Table of Contents</summary>

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Screenshots](#screenshots)
    
</details>


## Features

- Responsive pages and theming. Tested on Chrome, Firefox and Safari on Desktop, Android and Apple devices.
- Multiple different types of questions, with multimedia content, e.g. images, audio and video.
    - Text answers
    - Multiple Choice
    - Map selection
    - "Progressive questions": hints which reduce max score with each new hint
    - Google Trends, connects to the Google Trends API to automatically score based on the top search results.
- Different room codes.
- Live player list.

## Tech Stack
Python + Django, HTML, Javascript, Bootstrap, CSS, SQLite3, Redis with Django Channels.

Used Heroku for hosting.

## Screenshots
Quiz Title Page | End of Round Scores | Text Question
--- | --- | ---
<img width="350" alt="Quiz Title Page" src="https://user-images.githubusercontent.com/25383436/154982701-e9f2bb19-5482-4912-b095-6ef25ef369d6.png">|<img width="350" alt="End of Round Scores" src="https://user-images.githubusercontent.com/25383436/154984330-e8b79169-08c3-4ac7-935e-f4c2bf65d3f5.gif">|<img width="350" alt="Text Question" src="https://user-images.githubusercontent.com/25383436/154983029-82b91fa1-0df5-489d-96cb-d9a0001229d3.png">

Multiple Choice Question | Image Question with Answers | Audio Question
--- | --- | ---
<img width="350" alt="Multiple Choice Question" src="https://user-images.githubusercontent.com/25383436/154983157-3bd249f9-969c-4a05-baee-05116c1116f3.png">|<img width="350" alt="Image Question with Answers" src="https://user-images.githubusercontent.com/25383436/154983228-5fe1583f-df67-4c99-9c4f-97c534d50205.png">|<img width="350" alt="Audio Question" src="https://user-images.githubusercontent.com/25383436/154983268-bad3dd01-8f95-4f11-b75b-aceca3f3097d.png">

Google Trends Question | Ordering Question | Map Question
--- | --- | ---
<img width="640" alt="Screenshot 2022-03-07 at 1 31 48 pm" src="https://user-images.githubusercontent.com/25383436/157043916-d5119e91-975b-44a0-a47f-96d5de56f771.png">|<img width="350" alt="Ordering Question" src="https://user-images.githubusercontent.com/25383436/154984975-579869e1-4436-4878-a5b9-76e591f1f832.gif">|<img width="350" alt="Map Question" src="https://user-images.githubusercontent.com/25383436/154985041-b9f87bce-08b8-49f0-8b68-1046e50d4af2.png">

Progressive (Hints) Question | Progressive Image Question
--- | ---
<img width="350" alt="Progressive Question" src="https://user-images.githubusercontent.com/25383436/154992461-92bf148b-b189-4f26-b03a-f919b551abb9.gif">|<img width="350" alt="Progressive Image Question" src="https://user-images.githubusercontent.com/25383436/154992705-810a5cbb-4c78-4632-b596-6dbfdd956290.gif">
