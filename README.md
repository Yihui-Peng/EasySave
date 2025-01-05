# EasySave: Student Financial Planner


## Description

EasySave is a web-based app that aims to educate and assist students in creating personalized savings plans by analyzing their past spending behavior and providing actionable insights. The software will give personalized recommendations on saving, compare users' spending to peers, and offer a daily spending limit in order to allow users to reach their savings goals.

## Features
- **Personalized Savings Plans**: Tailored recommendations based on your income and spending habits.
- **Daily Spending Limit**: Automatically calculated to help you stay within your savings goals.
- **Real-Time Updates**: Graphics and data automatically update as you log new spending.
- **Peer Comparison**: Compare your spending habits with others in the same demographic.
- **Goal Tracking**: Set and monitor savings goals with interactive progress indicators.
- **Spending Predictions**: Forecast next month’s spending based on historical data.


## Table of Contents

1. Installation
2. Usage
3. Demo
4. Testing
5. License
6. Authors and Acknowledgment
7. Roadmap
8. Support

## Installation
To run this app locally:

1. Clone the repository:

```
git clone https://git.liacs.nl/group_6_sd/my-awesome-project.git
cd my-awesome-project
```

2. Install dependencies:

```
python -m venv venv
source venv/bin/activate  # For Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

3. Run the application:

Start the local server:
```
python app.py
```

4. Access the app:
Open your browser and navigate to:
http://127.0.0.1:5000/


## Usage

### Home Page  
An overview of spending and savings progress, featuring:  
- A progress circle that fills as users log spending.  
- A daily spending limit calculated from historical data to help users stay within their budget.  
- Interactive progress visualization for reaching savings goals.  

### Saving Goal Page  
Manage saving goals with visual trackers, including:  
- Viewing current saving goals with their progress.  
- Adding new goals by setting:  
  - Goal name.  
  - Start and end dates.  
  - Desired saving amount.  
  - Goal status (e.g., "In Progress" or "Finished").  

### Detailed Data Page  
Analyze spending trends and habits with graphical visualizations:  
- View spending records in an interactive graph.  
- Analyze monthly spending in categorized graphs.  
- Use filters to focus on specific spending categories.  


### Predictions Page  
Explore future spending predictions:  
- View predicted spending for the next month based on historical data.  
- Gain insights into saving and spending patterns for better financial planning.  

### User Profile  
Update personal account information, such as:  
- Name, gender, nickname, and age.  
- Email address and profile picture.  
- Any updates are directly reflected in the app's database.  


## Demo

[Click here to watch the demo video.](https://leidenuniv1-my.sharepoint.com/:v:/g/personal/s3990788_vuw_leidenuniv_nl/EWQqtigp00xGjRqCbi2F1q8B63BJgNNwN9CLoWdJs7FKsg?e=0y7rta)

## Testing

### Path_test_combined.py

Before running Path_test_combined.py, you must delete the data.db file in the instance folder. Once the test is done, you must once again delete the data.db file in order to be able to run the app.py file again.

### Coverage_test.py

In order to run the Coverage_test.py file correctly, you must first launch the app in the browser, and then run the test.

## License 
This project is part of a university assignment and is intended for academic use only. It is not licensed for public use or distribution.

## Authors and Acknowledgment
This project was jointly developed by: 

- Hao Chen - 3990788

- Adrien Im - 3984389

- Yihui Peng - 3985571

- Tony Tian - 3795888

- Zhemin Xie - 3808440

- Jiajia Xu - 3845567

The project was undertaken as part of the course *4032SWDEV: Software Development* at Leiden University, 
within the second-year curriculum of the Bachelor of Science in Data Science and Artificial Intelligence program.

Special thanks to our course instructor Dr. A. Saxena and our TA Aart for their guidance.

## Roadmap
Future improvements to this project could include:
- Greater compatibility across different devices
- Support for multiple currencies
- Advance analytics
- Community features

## Support
For help, you can reach us by email at: