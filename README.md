# openMV4-Proj
Self projects using openMV4 H7 Plus or K210 chip by Kaiser Ku. Including Electronics Design Contests in China.
## Proj1 : Design of a Tic-Tac-Toe Game Device
### General intro
From the 2024 National Undergraduate Electronics Design Competition Regional Contest (2024/7/29-2024/8/1).  
I represented ZJU in the competition choosing [Question E](https://res.nuedc-training.com.cn/topic/2024/topic_113.html).  
I served as the visual recognition specialist and report writer in the team.
### OpenMV Func
Using the openMV4 H7 Plus as the core of the image recognition system, it achieves the recognition and image locking of black and white chess pieces, forms a chessboard array from the coordinates of the separated black and white pieces, and calculates the playing strategy using an efficient Minimax decision tree algorithm based on the array coordinates. At the same time, it outputs the playing strategy and coordinates to the STM32F407VE microcontroller through the USART serial port, enabling the mechanical arm to perform the chess-playing operation.
### Conclusion & Insights
Overall, it's actually not too difficult, once you find the algorithm and then utilize Python libraries. The next step is to design how to update the chessboard using arrays. After updating, you just need to detect and output via the serial port, while paying attention to the setting of flag bits and the configuration of the ROI.  
The main difficulty lies in the parameter tuning of visual recognition to achieve accurate range and color identification, and the most challenging part is the communication with the STM32 and the robotic arm, which our team spent at least 12 hours on it (probably due to lack of experience).
