# ccviz

관련 논문: [A Fast Detecting Method for Clone Functions Using Global Alignment of Token Sequences](https://dl.acm.org/doi/10.1145/3383972.3384014)

위 논문을 만드는데 필요한 연구 과정에서 시각화 프로그램 `ccviz`를 담당, 2 저자로 이름을 올림

연구는 프로젝트 두 개를 보내면 "클론 코드"를 찾아 시각화해 주는 툴을 만드는 것으로 진행됨.

(아마도) KISTI에서 발주를 받은 연구였던것으로 기억함

## 관련 에피소드
1저자님이 주는 모듈의 결과를 ccviz로 시각화하는 것이 내 일이었음. 토큰 시퀀스 얼라이먼트 알고리즘으로 "클론 코드"를 찾아내고, 
찾아낸 부분을 정리하여 저장한 데이터가 ccviz의 입력이었음. 그런데 여기서 그 "데이터"를 어떻게 표현할지가 문제였음.

연구실에서는 교수님의 (아마도 Unix) 철학에 따라, 단순한 텍스트 형식에 적절한 문법을 정의하여 데이터를 표현하는 것이 관례였음.
그러나 나는 이에 반대함. 직접 만든 텍스트 형식이 아니라 json 형식을 쓰자고 강력히 주장함. 이 때 나는 연구실에서 서열이 뒤에서 두번째였고,
선배님들은 당연히 처음에는 반대함. 반대 이유는 여러가지였음: 교수님이 허가해 주실까?(허가해 주심) 1저자의 알고리즘은 C++로 구현하는데
json 라이브러리를 붙이는 게 직접 짜는 것보다 힘들지 않나?(그래도 해 주심) 등등.

하지만 어지간해서는 관례를 따르는 내가 웬일로 강하게 주장을 하다보니 이 요청은 들어 줌. 특히 1저자 선배님이 흔쾌히 허락을 해 주시고 결국 C++의
json 라이브러리를 설치하심. 

이 결정이 도움이 되었다고 생각함. 왜냐하면 알고리즘의 결과를 정리하는 데이터의 규격이 이후 몇번 변경되었기 때문. json이 아니었다면 일이 더 늘어났을 것임.
물론 1저자 선배님이랑 그 때 일을 이야기해봐야 확실하지만... 아무튼 도움이 되었을 것이라 생각함.

## 코드
파이썬에서 함수형 프로그래밍을 이용하여 선언적 표현을 쓰긴 하는데 영 별로임. 코드가 제대로 안 나뉘어져 있고.. 아무튼 더러움.

게다가 Dockerfile이나 requirements.txt가 없는데, html을 생성하는 라이브러리가 지금 파이썬 버전(3.11)에서 작동을 안함. \
역시 파이썬이야 가차 없지. 아무튼 이 코드는 실행해 볼 수가 없음...

## 더 알아보고 싶다면
내가 이야기하는 거보다 대학 연구실에 문의해 보는 것이 빠를 것. 나는 대부분의 문서를 가지고 있지 않음. 하지만 가능하면 그러지 않았으면 한다. \
여기 참여했던 분들 특히 1저자 선배님 박사 과정 하느라 바쁜데 괴롭히지 말아주세요..
