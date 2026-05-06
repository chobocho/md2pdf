---
title: "Scheme 프로그래밍 완전 가이드"
subtitle: "기초 문법부터 고급 매크로·자료구조·알고리즘까지"
author: "조숭화"
date: "2026"
lang: ko
documentclass: book
geometry: a5paper, margin=18mm
mainfont: "Noto Serif CJK KR"
sansfont: "Noto Sans CJK KR"
monofont: "D2Coding"
toc: true
toc-depth: 3
numbersections: true
linkcolor: blue
---

\newpage

# 머리말

Scheme은 1975년 Gerald Jay Sussman과 Guy L. Steele Jr.가 MIT에서 만든 Lisp 방언이다.
"적은 규칙으로 큰 표현력을 얻는다"는 미니멀리즘 철학으로 설계되었으며,
오늘날까지 SICP(`Structure and Interpretation of Computer Programs`)의 교육 언어로,
또 함수형·메타프로그래밍 연구의 기반 언어로 사용되고 있다.

이 책은 다음 네 갈래를 한 권에 담았다.

1. **기초 문법** — 표현식, 정의, 제어 흐름, 재귀, I/O
2. **고급 문법** — 클로저, 꼬리호출, 연속(continuation), 매크로, 모듈
3. **자료 구조** — 페어/리스트, 벡터, 해시, 트리, 그래프
4. **알고리즘** — 정렬, 탐색, 그래프, 동적계획, 분할정복, 백트래킹

모든 예제는 R7RS-small 표준을 기준으로 작성되었으며,
Racket(`#lang r7rs`), Chez Scheme, Chibi-Scheme 등 어느 처리계에서도 그대로 동작한다.

> **표기 약속**
>
> - `;;` 은 Scheme 주석.
> - `> 식` 은 REPL 입력, 다음 줄은 출력.
> - 절차(procedure)와 함수(function)는 같은 의미로 쓴다.
> - 이 책은 식별자에 한국어를 거의 쓰지 않는다(처리계 호환성 때문).

\newpage

# 차례 (개요)

## 1부 기초 문법

1. Scheme 둘러보기
2. 환경 설정과 첫 실행
3. 표현식·평가·식별자
4. 수치와 산술
5. 불리언과 조건식
6. 문자·문자열·심볼
7. 절차 정의: `lambda`, `define`
8. 지역 바인딩: `let`, `let*`, `letrec`
9. 재귀와 반복
10. 입출력과 포트

## 2부 고급 문법

11. 고차 함수와 함수형 패턴
12. 클로저와 상태 캡슐화
13. 꼬리호출과 누적자(accumulator) 패턴
14. 연속(continuation)과 `call/cc`
15. 위생 매크로 `syntax-rules`
16. 저수준 매크로 `syntax-case` / `define-syntax`
17. 지연 평가 `delay` / `force` / 스트림
18. 예외 처리 `guard` / `raise`
19. 모듈과 라이브러리(R7RS `define-library`)
20. 다중 값 `values` / `call-with-values`

## 3부 자료 구조

21. 페어와 리스트 깊이 보기
22. 연관 리스트와 속성표
23. 벡터와 다차원 배열
24. 해시 테이블
25. 문자열 기반 자료구조
26. 레코드(`define-record-type`)
27. 트리: 이진트리, BST, AVL, 적흑트리
28. 힙(우선순위 큐)
29. 그래프 표현
30. 큐, 덱, 스택, 링버퍼

## 4부 알고리즘

31. 알고리즘 분석 기초(점근표기)
32. 정렬: 버블/삽입/선택/머지/퀵/힙/카운팅
33. 탐색: 선형/이진/보간
34. 분할 정복
35. 동적 계획법
36. 그리디
37. 백트래킹
38. 그래프: BFS/DFS/Dijkstra/Floyd/Kruskal
39. 문자열 알고리즘: KMP, 라빈-카프, 트라이
40. 수치·확률 알고리즘

## 부록

A. R7RS-small 표준 절차 색인
B. Racket과의 차이
C. 디버깅과 프로파일링
D. 더 읽을거리

\newpage
# 1부 기초 문법

\newpage

## 1장 Scheme 둘러보기

### 1.1 첫 인상

가장 먼저, Scheme은 **괄호의 언어**다. 모든 코드는 *표현식*(expression)이며,
모든 표현식은 괄호로 둘러싸여 *연산자, 피연산자* 순으로 적힌다.

```scheme
(+ 1 2)            ;; 3
(* 3 (+ 4 5))      ;; 27
(display "Hello")  ;; Hello
```

`(+ 1 2)`는 "+에 1과 2를 적용한다"고 읽는다.
이것을 **전위 표기법**(prefix notation)이라 부른다.
어색하게 보여도, 다음 두 가지 큰 이점이 있다.

1. **연산자 우선순위가 사라진다.** 모든 식의 평가 순서가 괄호로 결정된다.
2. **코드와 데이터가 같은 모양이 된다.** 이 성질을 *동형성*(homoiconicity)이라 하며,
   매크로(15장)의 토대가 된다.

### 1.2 6분 코스

```scheme
;; 변수
(define pi 3.141592653589793)

;; 함수
(define (square x) (* x x))
(define (circle-area r) (* pi (square r)))

;; 사용
(circle-area 5)   ;; 78.53981633974483

;; 분기
(define (abs-val n)
  (if (< n 0) (- n) n))

;; 재귀
(define (factorial n)
  (if (<= n 1) 1
      (* n (factorial (- n 1)))))

(factorial 10)    ;; 3628800

;; 리스트
(define xs '(1 2 3 4 5))
(map square xs)            ;; (1 4 9 16 25)
(filter odd? xs)           ;; (1 3 5)
(apply + xs)               ;; 15
```

이 한 페이지가 곧 Scheme의 90%다. 나머지는 이 패턴의 변주다.

### 1.3 다른 언어와의 비교

| 개념 | C | Python | Scheme |
| :--- | :--- | :--- | :--- |
| 변수 선언 | `int x = 10;` | `x = 10` | `(define x 10)` |
| 함수 정의 | `int f(int x) {...}` | `def f(x): ...` | `(define (f x) ...)` |
| 조건문 | `if (a) b; else c;` | `b if a else c` | `(if a b c)` |
| 반복 | `for/while` | `for/while` | 재귀 또는 `do` |
| 리스트 | 배열 | `[1,2,3]` | `'(1 2 3)` |

Scheme은 *반복문이 거의 없다*. 대부분의 반복은 **재귀**로 표현하고,
컴파일러가 그것을 *꼬리호출 최적화*(13장)로 점프 코드로 바꾼다.

### 1.4 학습 로드맵

```
1부(기초)  →  2부(고급)  →  3부(자료구조)
                  ↓              ↓
                  └─→ 4부(알고리즘) ←─┘
```

- 처음 읽는 독자: 1부를 차근차근, 매 절 끝의 **연습문제**를 손으로 풀어보라.
- C/Python 경험자: 1장~3장을 빠르게 훑고 7장(절차)부터 깊게.
- SICP를 본 적 있는 독자: 2부와 4부 위주로 읽어도 좋다.

\newpage

## 2장 환경 설정과 첫 실행

### 2.1 처리계 고르기

이 책은 **Racket**을 기본 처리계로 권한다.

| 처리계 | 강점 | 설치 |
| :--- | :--- | :--- |
| Racket | 풍부한 라이브러리, 우수한 IDE(DrRacket) | `https://download.racket-lang.org` |
| Chez Scheme | 매우 빠름, R6RS 표준 준수 | `apt install chezscheme` |
| Guile | GNU/Emacs 통합 | `apt install guile-3.0` |
| Chibi | 임베디드용 경량 | `make && make install` |
| MIT/GNU | SICP 표준 | `apt install mit-scheme` |

### 2.2 Racket 설치 후 첫 실행

#### REPL

```
$ racket
Welcome to Racket v8.x
> (+ 1 2)
3
> (define (greet name) (string-append "안녕, " name "!"))
> (greet "세상")
"안녕, 세상!"
> ,exit
```

#### 파일 실행

`hello.rkt` 라는 파일을 만들고:

```scheme
#lang r7rs
(import (scheme base) (scheme write))
(display "Hello, Scheme!") (newline)
```

실행:

```
$ racket hello.rkt
Hello, Scheme!
```

`#lang r7rs` 첫 줄은 *이 파일을 R7RS 표준으로 읽으라*는 Racket 지시문이다.
순수 Scheme 처리계(Chez, Guile)에서는 이 줄을 빼면 된다.

### 2.3 편집기 설정

#### Emacs

```elisp
(use-package geiser-racket :ensure t)
;; M-x run-geiser → racket 선택
;; C-c C-z 로 REPL, C-M-x 로 식 단위 평가
```

#### VS Code

확장 `Magic Racket` 설치. 단축키:
- `Alt+Enter` 현재 식 평가
- `F5` 파일 실행

#### Termux(안드로이드)

```
pkg install racket
```

설치 후 `racket` 명령으로 REPL 진입. 이 책은 Termux 환경에서 모두 검증되었다.

### 2.4 책 예제 따라하기 규칙

- `;; ⇒` 는 식의 결과값 표시 — 직접 입력해 결과를 확인하라.
- `;; →` 는 출력(stdout) 표시.
- `;; !!` 는 의도적 오류 — 어떤 오류 메시지가 뜨는지 확인할 것.

```scheme
(+ 1 2)            ;; ⇒ 3
(display "hi")     ;; → hi
(/ 1 0)            ;; !! division by zero
```

### 2.5 연습문제

1. Racket을 설치하고 `(+ 1 2 3 4 5)`의 값을 확인하라.
2. `(display "내 이름은 ___입니다.")`를 자기 이름으로 채워 실행하라.
3. `pi`라는 이름에 3.14를 정의하고 `(* pi 2 5)`로 둘레를 계산하라.

\newpage

## 3장 표현식·평가·식별자

### 3.1 표현식과 값

Scheme의 모든 코드는 **표현식**이다. 표현식은 *평가*(evaluate)되어 **값**이 된다.

| 표현식 | 평가 결과(값) |
| :--- | :--- |
| `42` | 정수 42 |
| `"hi"` | 문자열 "hi" |
| `#t` | 참 |
| `#\A` | 문자 A |
| `'foo` | 심볼 foo |
| `(+ 1 2)` | 정수 3 |
| `(lambda (x) x)` | 절차 객체 |

평가 규칙은 정확히 세 가지다.

1. **자기평가형**(self-evaluating): 수, 문자열, 불리언, 문자는 자기 자신을 값으로 가진다.
2. **이름 참조**: 식별자(이름)는 환경에서 찾은 값으로 평가된다.
3. **조합**(combination): `(연산자 인자1 인자2 ...)` 꼴은
   - 연산자와 인자를 모두 평가한 뒤,
   - 연산자의 값(절차)을 인자들의 값에 *적용*한다.

```scheme
;; 자기평가형
42        ;; ⇒ 42
"hi"      ;; ⇒ "hi"

;; 이름
(define x 10)
x         ;; ⇒ 10

;; 조합
(* (+ 1 2) (- 5 1))  ;; ⇒ 12
```

### 3.2 특수형(special form)

조합 평가 규칙의 **예외**가 되는 식이 있다. 이것을 *특수형*이라 부른다.
대표적인 특수형: `define`, `if`, `lambda`, `quote`, `let`, `cond`, `and`, `or`, `set!`.

특수형은 인자들을 *항상 평가하지는 않는다*.
예를 들어 `(if 조건 참부분 거짓부분)`은 조건만 먼저 평가하고
참부분/거짓부분 중 한쪽만 평가한다.

```scheme
(if #t 1 (/ 1 0))   ;; ⇒ 1   ; (/ 1 0)은 평가되지 않음
```

### 3.3 식별자(identifier)와 명명 규칙

식별자에는 다음 문자가 허용된다:
- 영문자 대소문자, 숫자(첫 글자는 숫자 금지)
- `! $ % & * + - . / : < = > ? @ ^ _ ~`

관례:
- 단어 구분은 `-`(하이픈) 사용 — `make-list`, `string-length`.
- 술어(predicate)는 `?` 로 끝남 — `null?`, `pair?`, `even?`.
- 부작용 절차는 `!` 로 끝남 — `set!`, `vector-set!`.
- 형 변환은 `->` 로 — `string->number`, `list->vector`.

```scheme
(define max-iter 100)
(define empty-list? null?)
(string->number "42")    ;; ⇒ 42
```

### 3.4 환경(environment)

환경은 *식별자 → 값* 매핑이다. `define`은 현재 환경에 새 결합을 추가한다.

```scheme
(define a 1)
(define b 2)
(+ a b)   ;; ⇒ 3
```

`set!`은 *기존* 결합의 값을 바꾼다 — 없는 이름에 `set!` 하면 오류.

```scheme
(define n 5)
(set! n 10)
n         ;; ⇒ 10
(set! m 1) ;; !! unbound identifier
```

### 3.5 인용(quote)

식을 *평가하지 않고* 데이터로 다루려면 인용한다.

```scheme
(+ 1 2)        ;; ⇒ 3
(quote (+ 1 2)) ;; ⇒ (+ 1 2)   ; 세 원소짜리 리스트
'(+ 1 2)       ;; 위와 동일 (축약 표기)
'foo           ;; ⇒ foo  (심볼)
```

`'X` 는 `(quote X)`의 축약이다.

### 3.6 주석

```scheme
; 한 줄 주석 (R5RS 이전)
;; 한 줄 주석 (관례: 두 개)
;;; 절 단위 큰 주석

#| 여러 줄
   주석 (R6RS+) |#

#;(평가하지 않을 식)   ; datum 주석 (R7RS)
```

### 3.7 연습문제

1. `(define x (+ 2 3))` 후 `x`의 값을 확인하라.
2. `'(1 2 3)`과 `(list 1 2 3)`의 결과는? 둘은 같은 값인가?
3. `(if 0 'yes 'no)` 의 결과를 예상하고 직접 확인하라.
   (힌트: Scheme에서 `0`은 거짓이 아니다.)
4. `set!`로 정의되지 않은 변수의 값을 바꾸려 하면 어떤 오류가 나는가?

\newpage

## 4장 수치와 산술

### 4.1 수의 탑(numeric tower)

Scheme은 5단 수치 위계를 가진다.

```
 number
   └─ complex          (a+bi)
        └─ real        (3.14)
             └─ rational  (1/3)
                  └─ integer  (42)
```

상위 형은 하위 형을 포함한다. 모든 정수는 유리수이고, 모든 유리수는 실수다.

```scheme
(integer? 3)        ;; ⇒ #t
(rational? 1/3)     ;; ⇒ #t
(real? 3.14)        ;; ⇒ #t
(complex? 3+4i)     ;; ⇒ #t   (R7RS는 선택)
(number? "3")       ;; ⇒ #f
```

### 4.2 정확수(exact)와 비정확수(inexact)

Scheme의 수는 **정확/비정확** 두 가지 *정밀도 표시*를 가진다.

```scheme
(exact? 3)        ;; ⇒ #t   ; 정수는 정확
(exact? 1/3)      ;; ⇒ #t   ; 유리수도 정확
(exact? 3.14)     ;; ⇒ #f   ; 부동소수점은 비정확
(exact? 3.0)      ;; ⇒ #f
```

상호 변환:

```scheme
(exact->inexact 1/3)   ;; ⇒ 0.3333333333333333
(inexact->exact 0.5)   ;; ⇒ 1/2
(inexact 1/3)          ;; ⇒ 0.333... (R7RS 줄임이름)
(exact 0.5)            ;; ⇒ 1/2
```

연산 규칙: 정확과 비정확이 섞이면 결과는 *비정확*이다.

```scheme
(+ 1 2)        ;; ⇒ 3       (정확)
(+ 1 2.0)      ;; ⇒ 3.0     (비정확)
(/ 1 3)        ;; ⇒ 1/3     (정확)
(/ 1.0 3)      ;; ⇒ 0.333.. (비정확)
```

### 4.3 산술 절차

```scheme
(+ 1 2 3 4)     ;; ⇒ 10
(- 10 3 2)      ;; ⇒ 5
(* 2 3 4)       ;; ⇒ 24
(/ 12 3 2)      ;; ⇒ 2

;; 0/1 인자
(+)             ;; ⇒ 0
(*)             ;; ⇒ 1
(- 5)           ;; ⇒ -5  (단항 -는 부호 반전)
(/ 5)           ;; ⇒ 1/5 (단항 /는 역수)
```

#### 정수 나눗셈

```scheme
(quotient 17 5)     ;; ⇒ 3
(remainder 17 5)    ;; ⇒ 2
(modulo 17 5)       ;; ⇒ 2
(quotient -17 5)    ;; ⇒ -3
(remainder -17 5)   ;; ⇒ -2
(modulo -17 5)      ;; ⇒ 3   ; 결과 부호가 제수와 같음
```

`remainder`와 `modulo`의 차이: 음수에서 다르다. 일반적으로 수학적 나머지는 `modulo`.

#### 비교

```scheme
(< 1 2 3)       ;; ⇒ #t   (체인 비교 가능)
(= 1 1.0)       ;; ⇒ #t
(eqv? 1 1.0)    ;; ⇒ #f   ; 형이 다르면 다름
(zero? 0)       ;; ⇒ #t
(positive? -1)  ;; ⇒ #f
(odd? 3)        ;; ⇒ #t
```

#### 그 밖의 수치 절차

```scheme
(abs -7)             ;; ⇒ 7
(min 3 1 4 1 5)      ;; ⇒ 1
(max 3 1 4 1 5)      ;; ⇒ 5
(gcd 24 36)          ;; ⇒ 12
(lcm 6 8)            ;; ⇒ 24
(expt 2 10)          ;; ⇒ 1024
(sqrt 16)            ;; ⇒ 4
(sqrt 2)             ;; ⇒ 1.4142135623730951
(floor 3.7)          ;; ⇒ 3.0
(ceiling 3.2)        ;; ⇒ 4.0
(round 3.5)          ;; ⇒ 4.0   ; banker's rounding
(truncate 3.7)       ;; ⇒ 3.0
(exp 1)              ;; ⇒ 2.718281828459045
(log 2.718)          ;; ⇒ 0.999...
(sin 0) (cos 0)      ;; ⇒ 0  1
```

### 4.4 수치 리터럴

```scheme
42          ;; 정수
-3          ;; 음수
1/3         ;; 유리수
3.14        ;; 부동소수점
1e3         ;; 1000.0 (지수 표기)
#e3.14      ;; 정확화 → 157/50
#i1/3       ;; 비정확화 → 0.333...
#b1010      ;; 2진수 ⇒ 10
#o17        ;; 8진수 ⇒ 15
#xFF        ;; 16진수 ⇒ 255
```

### 4.5 문자열↔수 변환

```scheme
(number->string 42)           ;; ⇒ "42"
(number->string 255 16)       ;; ⇒ "ff"
(number->string 10 2)         ;; ⇒ "1010"
(string->number "42")         ;; ⇒ 42
(string->number "ff" 16)      ;; ⇒ 255
(string->number "abc")        ;; ⇒ #f   ; 실패시 거짓
```

### 4.6 부동소수점 함정

다른 언어와 같은 함정을 공유한다.

```scheme
(= 0.1 (* 0.1 1))            ;; ⇒ #t
(= (+ 0.1 0.2) 0.3)          ;; ⇒ #f
(- (+ 0.1 0.2) 0.3)          ;; ⇒ 5.55e-17
```

해법: 정확수로 작업하다 마지막에만 비정확화.

```scheme
(= (+ 1/10 2/10) 3/10)       ;; ⇒ #t
```

### 4.7 실전 예제 — 원의 넓이

```scheme
(define pi 3.141592653589793)

(define (square x) (* x x))

(define (circle-area r)
  (* pi (square r)))

(circle-area 5)        ;; ⇒ 78.53981633974483
```

### 4.8 실전 예제 — 이차방정식 근

```scheme
(define (quadratic-roots a b c)
  (let ((d (- (* b b) (* 4 a c))))
    (if (negative? d)
        (list 'complex)
        (let ((s (sqrt d)))
          (list (/ (+ (- b) s) (* 2 a))
                (/ (- (- b) s) (* 2 a)))))))

(quadratic-roots 1 -3 2)   ;; ⇒ (2.0 1.0)
(quadratic-roots 1 0 1)    ;; ⇒ (complex)
```

### 4.9 연습문제

1. 화씨를 섭씨로 바꾸는 `f->c`를 정의하라.
2. 두 정수의 *평균*을 구하는 `mean2`를 정의하되, 정수 두 개의 평균이
   유리수가 되도록 하라. (힌트: `/`만 쓰고 `quotient`는 쓰지 말 것)
3. 거듭제곱 `(my-expt b n)`을 곱셈만으로 정의하라(반복 곱).
4. 다섯 수의 표준편차를 구하는 `stddev5`를 작성하라.

\newpage

## 5장 불리언과 조건식

### 5.1 진리값

Scheme의 진리값은 단 두 개: `#t`(참)과 `#f`(거짓).
중요한 규칙: **`#f`만 거짓이고, 그 외 모든 값은 참이다.**

```scheme
(if 0 'T 'F)        ;; ⇒ T   ; 0도 참
(if "" 'T 'F)       ;; ⇒ T   ; 빈 문자열도 참
(if '() 'T 'F)      ;; ⇒ T   ; 빈 리스트도 참 (R7RS)
(if #f 'T 'F)       ;; ⇒ F
```

> 주의: R5RS 이전에는 `'()`도 거짓으로 간주하는 처리계가 있었다. 지금은 통일되었다.

### 5.2 논리 연산자

`and`, `or`은 단락 평가(short-circuit)하며,
`#t/#f`가 아니라 *마지막으로 평가된 값*을 돌려준다.

```scheme
(and 1 2 3)         ;; ⇒ 3
(and 1 #f 3)        ;; ⇒ #f
(or #f 'yes 'no)    ;; ⇒ yes
(or #f #f)          ;; ⇒ #f
(not #f)            ;; ⇒ #t
(not 0)             ;; ⇒ #f
(and)               ;; ⇒ #t   (단위원)
(or)                ;; ⇒ #f
```

이 성질은 자주 쓰인다.

```scheme
;; "x가 음수가 아니면 sqrt, 아니면 #f"
(define (safe-sqrt x)
  (and (>= x 0) (sqrt x)))

(safe-sqrt 16)   ;; ⇒ 4
(safe-sqrt -1)   ;; ⇒ #f
```

### 5.3 `if`

```scheme
(if 조건 참부분)
(if 조건 참부분 거짓부분)
```

거짓부분이 빠지면 R7RS는 *명세되지 않은 값*을 돌려준다 — 그 결과를 사용하지 말라.

```scheme
(define (sgn x)
  (if (positive? x)  1
   (if (negative? x) -1 0)))

(sgn -5)   ;; ⇒ -1
(sgn 0)    ;; ⇒ 0
(sgn 5)    ;; ⇒ 1
```

### 5.4 `cond`

다중 분기에는 `cond`가 자연스럽다.

```scheme
(cond
  (조건1 식1 ...)
  (조건2 식2 ...)
  ...
  (else 기본식 ...))
```

```scheme
(define (grade s)
  (cond ((>= s 90) 'A)
        ((>= s 80) 'B)
        ((>= s 70) 'C)
        ((>= s 60) 'D)
        (else 'F)))

(grade 85)   ;; ⇒ B
```

#### `=>` 화살표

`(조건 => 절차)`는 조건 값이 참이면 그 값을 절차에 적용한다.

```scheme
(define alist '((a . 1) (b . 2) (c . 3)))

(cond ((assq 'b alist) => cdr)
      (else 'not-found))
;; ⇒ 2
```

`(assq 'b alist)`가 `(b . 2)`를 돌려주면, 그 값을 `cdr`에 적용해 `2`를 얻는다.

### 5.5 `when` / `unless`

부작용용 단방향 분기.

```scheme
(when (> x 100)
  (display "큰 수입니다") (newline))

(unless (zero? x)
  (display (/ 1 x)))
```

`when 조건 식들`은 `(if 조건 (begin 식들))`의 축약이고,
`unless`는 그 반대.

### 5.6 `case`

같음(`eqv?`) 비교가 필요한 다중 분기.

```scheme
(define (describe-day d)
  (case d
    ((mon tue wed thu fri) 'weekday)
    ((sat sun)             'weekend)
    (else                  'unknown)))

(describe-day 'wed)   ;; ⇒ weekday
(describe-day 'sat)   ;; ⇒ weekend
```

### 5.7 술어(predicate)

| 술어 | 설명 |
| :--- | :--- |
| `boolean?` | `#t`/`#f` 인가 |
| `number?` | 수인가 |
| `integer?` | 정수인가 |
| `pair?` | 페어인가 (빈 리스트 제외) |
| `null?` | 빈 리스트인가 |
| `list?` | 정상 리스트인가 |
| `string?` | 문자열인가 |
| `symbol?` | 심볼인가 |
| `procedure?` | 절차인가 |
| `eq?` | 동일 객체인가 (포인터 비교) |
| `eqv?` | 같은 값인가 (수/문자 포함) |
| `equal?` | 구조적으로 같은가 (재귀 비교) |

```scheme
(eq? 'a 'a)              ;; ⇒ #t
(eq? '(1 2) '(1 2))      ;; ⇒ 처리계 의존(보통 #f)
(eqv? 1 1.0)             ;; ⇒ #f
(equal? '(1 2) '(1 2))   ;; ⇒ #t
```

**규칙**: 의심스러우면 `equal?`를 써라. 내부적으로 `eq?`/`eqv?`를 적절히 호출한다.
다만 `equal?`는 재귀 비교이므로 큰 자료에는 비싸다.

### 5.8 실전 예제 — 윤년 판정

```scheme
(define (leap-year? y)
  (and (zero? (modulo y 4))
       (or (not (zero? (modulo y 100)))
           (zero? (modulo y 400)))))

(leap-year? 2000)   ;; ⇒ #t
(leap-year? 1900)   ;; ⇒ #f
(leap-year? 2024)   ;; ⇒ #t
(leap-year? 2025)   ;; ⇒ #f
```

### 5.9 실전 예제 — 가위바위보

```scheme
(define (rps-judge a b)
  (cond ((eq? a b) 'tie)
        ((or (and (eq? a 'rock)     (eq? b 'scissors))
             (and (eq? a 'scissors) (eq? b 'paper))
             (and (eq? a 'paper)    (eq? b 'rock)))
         'a-wins)
        (else 'b-wins)))

(rps-judge 'rock 'scissors)   ;; ⇒ a-wins
(rps-judge 'paper 'paper)     ;; ⇒ tie
(rps-judge 'scissors 'rock)   ;; ⇒ b-wins
```

### 5.10 연습문제

1. 세 수 중 가장 큰 수를 돌려주는 `max3`을 `if`만으로 정의하라.
2. `cond`로 동물의 다리 수 분류기 `legs`를 만들어라
   (`'dog`/`'cat`/`'human`/`'spider`/`'snake`).
3. `xor`(둘 중 정확히 하나만 참) 절차를 정의하라.
4. `(implies a b)` (a가 참이면 b가 참인지)를 `or`/`not`만 써서 정의하라.

\newpage

## 6장 문자·문자열·심볼

### 6.1 문자

문자 리터럴은 `#\X` 형식.

```scheme
#\A              ;; 문자 A
#\a              ;; 문자 a
#\space          ;; 공백
#\newline        ;; 개행
#\tab            ;; 탭
#\null           ;; NUL
#\x41            ;; 16진 코드포인트 ⇒ 'A'
```

#### 절차

```scheme
(char->integer #\A)    ;; ⇒ 65
(integer->char 97)     ;; ⇒ #\a
(char-upcase #\a)      ;; ⇒ #\A
(char-downcase #\A)    ;; ⇒ #\a
(char-alphabetic? #\a) ;; ⇒ #t
(char-numeric? #\5)    ;; ⇒ #t
(char-whitespace? #\ ) ;; ⇒ #t
(char<? #\a #\b)       ;; ⇒ #t
(char=? #\a #\a)       ;; ⇒ #t
```

### 6.2 문자열

```scheme
"안녕"             ;; 문자열
""                 ;; 빈 문자열
"줄\n바꿈"          ;; 이스케이프
"따옴표 \"안\""    ;; 따옴표 이스케이프
"백슬래시 \\"      ;; 백슬래시
```

#### 만들기와 변환

```scheme
(make-string 5 #\*)         ;; ⇒ "*****"
(string #\h #\i)            ;; ⇒ "hi"
(list->string '(#\h #\i))   ;; ⇒ "hi"
(string->list "hi")         ;; ⇒ (#\h #\i)
(symbol->string 'foo)       ;; ⇒ "foo"
(string->symbol "foo")      ;; ⇒ foo
```

#### 길이·접근

```scheme
(string-length "abc")       ;; ⇒ 3
(string-ref "abc" 0)        ;; ⇒ #\a
(string-ref "abc" 2)        ;; ⇒ #\c
```

#### 결합·자르기

```scheme
(string-append "hi, " "world")   ;; ⇒ "hi, world"
(substring "abcdef" 1 4)         ;; ⇒ "bcd"

;; R7RS는 [start, end) 반개구간
```

#### 비교

```scheme
(string=? "abc" "abc")     ;; ⇒ #t
(string<? "abc" "abd")     ;; ⇒ #t
(string-ci=? "ABC" "abc")  ;; ⇒ #t   ; 대소문자 무시
```

#### 변환·복사

```scheme
(string-upcase "abc")      ;; ⇒ "ABC"
(string-downcase "ABC")    ;; ⇒ "abc"
(string-copy "abcdef" 1 4) ;; ⇒ "bcd"
```

#### 가변 문자열

`make-string`이나 `string-copy`로 만든 문자열은 가변이다.
리터럴 `"abc"`는 *상수*이므로 변경하면 오류.

```scheme
(define s (make-string 3 #\x))
(string-set! s 1 #\Y)
s                ;; ⇒ "xYx"

(string-set! "abc" 0 #\Z)   ;; !! immutable
```

### 6.3 문자열 검색·분할 (라이브러리 SRFI-13)

R7RS small에는 빠져 있어 직접 구현하거나 `(scheme charset)` / SRFI를 쓴다.

```scheme
;; 직접 구현: 문자 위치 찾기
(define (string-index s c)
  (let loop ((i 0))
    (cond ((>= i (string-length s)) #f)
          ((char=? (string-ref s i) c) i)
          (else (loop (+ i 1))))))

(string-index "hello" #\l)   ;; ⇒ 2

;; 직접 구현: 분리자 기반 분할
(define (string-split s sep)
  (let loop ((chars (string->list s)) (acc '()) (cur '()))
    (cond ((null? chars)
           (reverse (cons (list->string (reverse cur)) acc)))
          ((char=? (car chars) sep)
           (loop (cdr chars)
                 (cons (list->string (reverse cur)) acc)
                 '()))
          (else
           (loop (cdr chars) acc (cons (car chars) cur))))))

(string-split "a,b,,c" #\,)   ;; ⇒ ("a" "b" "" "c")
```

### 6.4 심볼

심볼은 *이름이 곧 정체성*인 원자값이다.

```scheme
'foo             ;; 심볼 foo
'hello-world     ;; 심볼 hello-world
'|with space|    ;; (R7RS) 공백 포함 심볼
```

#### 비교·변환

```scheme
(eq? 'foo 'foo)             ;; ⇒ #t   (심볼은 internalize됨)
(symbol? 'foo)              ;; ⇒ #t
(symbol->string 'foo)       ;; ⇒ "foo"
(string->symbol "BAR")      ;; ⇒ BAR
(eq? (string->symbol "x")
     (string->symbol "x"))  ;; ⇒ #t
```

심볼은 *해시 키*나 *식별 태그*로 매우 유용하다.

```scheme
;; 색상 태그
(define color 'red)
(case color
  ((red)   "#ff0000")
  ((green) "#00ff00")
  ((blue)  "#0000ff"))
```

### 6.5 실전 예제 — 회문(palindrome) 판정

```scheme
(define (palindrome? s)
  (let* ((n (string-length s))
         (half (quotient n 2)))
    (let loop ((i 0))
      (cond ((>= i half) #t)
            ((char=? (string-ref s i)
                     (string-ref s (- n 1 i)))
             (loop (+ i 1)))
            (else #f)))))

(palindrome? "racecar")    ;; ⇒ #t
(palindrome? "hello")      ;; ⇒ #f
(palindrome? "")           ;; ⇒ #t
```

### 6.6 실전 예제 — 단어 수 세기

```scheme
(define (count-words s)
  (let loop ((chars (string->list s)) (in-word? #f) (n 0))
    (cond ((null? chars) (if in-word? (+ n 1) n))
          ((char-whitespace? (car chars))
           (if in-word?
               (loop (cdr chars) #f (+ n 1))
               (loop (cdr chars) #f n)))
          (else
           (loop (cdr chars) #t n)))))

(count-words "the quick brown fox")   ;; ⇒ 4
(count-words "  hello   world  ")     ;; ⇒ 2
```

### 6.7 연습문제

1. 문자열을 뒤집는 `string-reverse`를 작성하라.
2. 영문 알파벳만 걸러내는 `letters-only`를 작성하라.
3. 카이사르 암호 `(caesar s n)` — 알파벳을 n만큼 시프트.
4. 단어를 빈도 내림차순으로 정렬한 alist를 만드는 `word-freq`를 작성하라.
   (3부에서 더 좋은 방법으로 다시 풀어볼 것이다.)

\newpage

## 7장 절차 정의: `lambda`, `define`

### 7.1 `lambda`

`lambda`는 *익명 절차*를 만든다.

```
(lambda (매개변수목록) 본문...)
```

```scheme
((lambda (x) (* x x)) 5)            ;; ⇒ 25
((lambda (x y) (+ x y)) 3 4)        ;; ⇒ 7
((lambda () 42))                    ;; ⇒ 42  (인자 없음)
```

### 7.2 `define`로 이름 붙이기

다음 두 정의는 동치다.

```scheme
(define square (lambda (x) (* x x)))
(define (square x) (* x x))
```

후자가 *문법 설탕*. 본문이 둘 이상이면 순차 실행되고 마지막 값이 결과다.

```scheme
(define (greet name)
  (display "안녕, ")
  (display name)
  (newline)
  'done)

(greet "철수")
;; → 안녕, 철수
;; ⇒ done
```

### 7.3 매개변수 형태

#### 고정 매개변수

```scheme
(define (add a b) (+ a b))
(add 1 2)                       ;; ⇒ 3
(add 1)                         ;; !! 인자 부족
```

#### 가변 매개변수

전체를 한 리스트로 받음:

```scheme
(define (sum . args)
  (apply + args))

(sum 1 2 3 4)                   ;; ⇒ 10
(sum)                           ;; ⇒ 0
```

고정 + 나머지:

```scheme
(define (head-and-rest h . t)
  (list 'head h 'rest t))

(head-and-rest 1 2 3 4)         ;; ⇒ (head 1 rest (2 3 4))
```

### 7.4 절차도 값(first-class)이다

절차는 변수에 담고, 인자로 넘기고, 반환할 수 있다.

```scheme
(define f square)
(f 5)                           ;; ⇒ 25

;; 절차를 인자로
(define (twice fn x) (fn (fn x)))
(twice square 3)                ;; ⇒ 81

;; 절차를 반환
(define (adder n)
  (lambda (x) (+ x n)))

(define add5 (adder 5))
(add5 10)                       ;; ⇒ 15
```

이 *값으로서의 절차*가 함수형 프로그래밍의 핵심이다 (11장에서 깊이 다룬다).

### 7.5 본문 안의 정의(internal define)

`define`은 다른 절차 본문 안에서도 쓸 수 있다.
지역 보조 함수를 정의할 때 유용하다.

```scheme
(define (hypotenuse a b)
  (define (square x) (* x x))
  (sqrt (+ (square a) (square b))))

(hypotenuse 3 4)               ;; ⇒ 5.0
```

내부 `define`은 본문의 *맨 앞*에만 올 수 있다 (R7RS).

### 7.6 디폴트 인자(R6RS+ / SRFI-89)

R7RS-small에는 직접적 디폴트 인자가 없다. 대신 가변 인자로 흉내낸다.

```scheme
(define (greet name . rest)
  (let ((msg (if (null? rest) "안녕" (car rest))))
    (display msg) (display ", ") (display name) (newline)))

(greet "철수")           ;; → 안녕, 철수
(greet "영희" "헬로")     ;; → 헬로, 영희
```

### 7.7 키워드 인자(처리계 의존)

Racket·Chez는 키워드 인자를 지원한다. 이식성을 원하면 alist로 흉내낸다.

```scheme
(define (rect opts)
  (define (opt k d) (or (cdr (or (assq k opts) (cons #f d))) d))
  (let ((w (opt 'width 10))
        (h (opt 'height 5)))
    (* w h)))

(rect '((width . 4) (height . 3)))   ;; ⇒ 12
(rect '((width . 4)))                ;; ⇒ 20
```

### 7.8 도큐먼트 문자열

R7RS에는 표준 docstring이 없다. 절차 첫 식을 문자열로 두는 관례:

```scheme
(define (my-fn x)
  "x를 두 배 한다."   ; 평가만 되고 버려진다
  (* 2 x))
```

처리계에 따라 `(procedure-doc my-fn)`을 지원하기도 한다.

### 7.9 실전 예제 — 함수 합성

```scheme
(define (compose f g)
  (lambda (x) (f (g x))))

(define inc (lambda (x) (+ x 1)))
(define double (lambda (x) (* x 2)))

(define inc-then-double (compose double inc))
(inc-then-double 3)            ;; ⇒ 8

;; 가변 인자 합성
(define (compose* . fns)
  (cond ((null? fns) (lambda (x) x))
        ((null? (cdr fns)) (car fns))
        (else (compose (car fns)
                       (apply compose* (cdr fns))))))

((compose* double inc inc) 3)  ;; ⇒ 10
```

### 7.10 연습문제

1. `make-counter`: 호출할 때마다 1씩 증가하는 카운터를 만드는 절차를 작성하라.
   (힌트: `set!`와 클로저)
2. `(curry f)` — 두 인자 절차 `f`를 커리화한다 → `((curry f) 1 2)` = `(f 1 2)`,
   `(((curry f) 1) 2)` = `(f 1 2)`.
3. `flip`: 인자 순서를 뒤집는 절차. `((flip /) 2 10)` ⇒ 5.
4. 매개변수 *없는* 절차와 *빈 인자 호출*을 구분 가능한 코드를 짜보라.

\newpage

## 8장 지역 바인딩: `let`, `let*`, `letrec`

### 8.1 `let`: 병렬 바인딩

```
(let ((이름1 값1)
      (이름2 값2)
      ...)
  본문)
```

이름들은 **동시에** 바인딩된다 — 각 값식은 *바깥* 환경에서 평가된다.

```scheme
(let ((a 1) (b 2))
  (+ a b))                       ;; ⇒ 3

(define x 10)
(let ((x 1) (y x))               ; y는 바깥의 x(=10)
  (list x y))                    ;; ⇒ (1 10)
```

`let`은 사실 즉시 호출되는 람다의 설탕이다.

```scheme
(let ((x 1) (y 2)) (+ x y))
;; 와 동치
((lambda (x y) (+ x y)) 1 2)
```

### 8.2 `let*`: 순차 바인딩

각 이름은 *그 앞 이름들*을 볼 수 있다.

```scheme
(let* ((x 1) (y (+ x 1)) (z (+ y 1)))
  (list x y z))                  ;; ⇒ (1 2 3)
```

`let`이라면 `(+ x 1)`에서 x는 바깥에서 찾아야 하지만, `let*`은 안에서 찾는다.

### 8.3 `letrec`: 재귀 바인딩

상호 재귀가 필요할 때 — 각 이름은 *서로*를 볼 수 있다 (값을 평가할 때 아직 정의되지 않았을 수 있으므로 **값식 안에서 즉시 사용하면 안 된다**).

```scheme
(letrec ((even? (lambda (n) (if (zero? n) #t (odd? (- n 1)))))
         (odd?  (lambda (n) (if (zero? n) #f (even? (- n 1))))))
  (even? 10))                    ;; ⇒ #t
```

### 8.4 명명된 `let` (loop 패턴)

가장 유용한 Scheme 관용구 중 하나.

```
(let 이름 ((변수1 초기값1) ...) 본문)
```

이것은 *재귀 절차를 그 자리에서 정의하면서 첫 호출*까지 수행한다.

```scheme
(let loop ((i 0) (acc 0))
  (if (= i 10)
      acc
      (loop (+ i 1) (+ acc i))))
;; ⇒ 45
```

이는 다음과 동치다.

```scheme
((letrec ((loop (lambda (i acc)
                  (if (= i 10) acc
                      (loop (+ i 1) (+ acc i))))))
   loop)
 0 0)
```

### 8.5 `let-values` — 다중값 바인딩 (20장 참고)

```scheme
(define (div-mod a b) (values (quotient a b) (remainder a b)))

(let-values (((q r) (div-mod 17 5)))
  (list 'q q 'r r))              ;; ⇒ (q 3 r 2)
```

### 8.6 `begin` — 순차 실행

```scheme
(begin
  (display "1 ")
  (display "2 ")
  3)                             ;; → 1 2  ⇒ 3
```

`define`/`lambda` 본문은 암시적으로 `begin`이다.

### 8.7 실전 예제 — 평균과 분산

```scheme
(define (stats xs)
  (let* ((n (length xs))
         (sum (apply + xs))
         (mean (/ sum n))
         (sqsum (apply + (map (lambda (x) (* (- x mean) (- x mean))) xs)))
         (var (/ sqsum n)))
    (list 'n n 'mean mean 'var var)))

(stats '(1 2 3 4 5))
;; ⇒ (n 5 mean 3 var 2)
```

### 8.8 실전 예제 — 카드 한 벌 만들기

```scheme
(define (make-deck)
  (let loop-suit ((suits '(spade heart diamond club)) (deck '()))
    (if (null? suits)
        deck
        (let loop-rank ((ranks '(2 3 4 5 6 7 8 9 10 J Q K A))
                        (acc deck))
          (if (null? ranks)
              (loop-suit (cdr suits) acc)
              (loop-rank (cdr ranks)
                         (cons (cons (car suits) (car ranks)) acc)))))))

(length (make-deck))   ;; ⇒ 52
```

### 8.9 연습문제

1. `let`을 즉시 호출 람다로 손수 변환해 보라(2~3개의 예).
2. `letrec` 없이 상호 재귀 `even?`/`odd?`를 만들 수 있는가? 그렇다면 어떻게?
   (힌트: 한 절차가 자기 자신을 인자로 받는 *Y 콤비네이터* 흉내)
3. 명명된 `let`으로 1부터 100까지의 합을 내라.
4. 명명된 `let`으로 피보나치를 *반복* 형태로 작성하라(13장에 다시 등장).

\newpage

## 9장 재귀와 반복

### 9.1 재귀의 기본형

```scheme
(define (length* xs)
  (if (null? xs) 0
      (+ 1 (length* (cdr xs)))))

(length* '(a b c d))   ;; ⇒ 4
```

이 정의는 *선형 재귀*다 — 호출 깊이가 입력 길이에 비례.
호출이 n번 쌓이면 스택 메모리도 n에 비례한다.

### 9.2 누적자(accumulator) 패턴 = 꼬리 재귀

```scheme
(define (length** xs)
  (let loop ((xs xs) (n 0))
    (if (null? xs) n
        (loop (cdr xs) (+ n 1)))))
```

마지막 호출이 *그 절차 자체*이고, 호출의 결과를 그대로 반환하면 그것이 **꼬리 호출**이다.
Scheme 표준은 꼬리 호출을 *반드시 점프로 최적화*하도록 명령한다 — 스택 사용 O(1).

> 반대로, 위의 `(+ 1 (length* (cdr xs)))`은 꼬리 호출이 *아니다*. 호출 후 `+ 1`이 남기 때문.

### 9.3 트리 재귀

```scheme
(define (fib n)
  (if (< n 2) n
      (+ (fib (- n 1)) (fib (- n 2)))))

(fib 10)   ;; ⇒ 55
```

(fib 30)은 약 270만 번 호출된다 — 비효율. 13장에서 누적자로 O(n)을 만든다.

### 9.4 명령형 반복 — `do`

```
(do ((변수 초기값 갱신식) ...)
    (종료조건 결과식 ...)
  본문...)
```

```scheme
(do ((i 0 (+ i 1))
     (sum 0 (+ sum i)))
    ((= i 10) sum))
;; ⇒ 45
```

C의 `for(i=0; i<10; i++) sum += i; return sum;`와 유사하다.
`do`는 명명된 `let`으로 거의 항상 대체할 수 있다 — 취향대로.

### 9.5 사이드이펙트가 있는 반복

```scheme
(do ((i 1 (+ i 1)))
    ((> i 5))
  (display i) (display " "))
;; → 1 2 3 4 5
```

종료식의 결과식이 비면 *명세되지 않은 값*. 결과를 쓰지 말 것.

### 9.6 `for-each`와 `map`

리스트가 있다면 명시적 반복보다 *고차 함수*가 깔끔하다.

```scheme
(for-each display '(1 2 3))     ;; → 123
(for-each (lambda (x) (display x) (newline)) '(a b c))
;; → a
;;   b
;;   c

(map (lambda (x) (* x x)) '(1 2 3 4))   ;; ⇒ (1 4 9 16)
```

### 9.7 실전 — 거듭제곱 빠르게 (이분 거듭제곱)

```scheme
(define (fast-expt b n)
  (cond ((zero? n) 1)
        ((even? n) (square (fast-expt b (quotient n 2))))
        (else      (* b (fast-expt b (- n 1))))))

(define (square x) (* x x))

(fast-expt 2 30)   ;; ⇒ 1073741824
```

이 절차는 O(log n) 시간이지만 *꼬리 재귀가 아니다*. 누적자 버전:

```scheme
(define (fast-expt-iter b n)
  (let loop ((b b) (n n) (acc 1))
    (cond ((zero? n) acc)
          ((even? n) (loop (* b b) (quotient n 2) acc))
          (else      (loop b (- n 1) (* acc b))))))

(fast-expt-iter 2 30)   ;; ⇒ 1073741824
```

### 9.8 실전 — 유클리드 호제법

```scheme
(define (gcd* a b)
  (if (zero? b) a (gcd* b (modulo a b))))

(gcd* 252 105)   ;; ⇒ 21
```

이 정의는 자연스럽게 꼬리 재귀.

### 9.9 실전 — 리스트 뒤집기

```scheme
;; 단순 — O(n²) 시간 (각 단계마다 append!)
(define (reverse-naive xs)
  (if (null? xs) '()
      (append (reverse-naive (cdr xs)) (list (car xs)))))

;; 누적자 — O(n) 시간
(define (reverse* xs)
  (let loop ((xs xs) (acc '()))
    (if (null? xs) acc
        (loop (cdr xs) (cons (car xs) acc)))))

(reverse* '(1 2 3 4 5))   ;; ⇒ (5 4 3 2 1)
```

### 9.10 연습문제

1. `(count-down n)` — n부터 1까지 출력하는 절차.
2. `sum-list`를 단순 재귀와 꼬리 재귀 두 버전으로 작성하고
   큰 입력에서 성능 차를 관찰하라.
3. `(power-of-2? n)` — n이 2의 거듭제곱인지 판정.
4. `(digits n)` — 양의 정수 n을 자릿수 리스트로. (`digits 1024` ⇒ `(1 0 2 4)`)

\newpage

## 10장 입출력과 포트

### 10.1 표준 출력

```scheme
(display "hi")          ;; → hi   (사람이 읽는 형식)
(newline)               ;; → 개행
(write "hi")            ;; → "hi" (Scheme이 다시 읽을 수 있는 형식)
(write '(a "b" #\c))    ;; → (a "b" #\c)
```

`display`는 *프린트*, `write`는 *시리얼라이즈*에 해당한다.

### 10.2 표준 입력

```scheme
(read)              ;; 한 식을 읽어 값으로
(read-char)         ;; 한 글자
(read-line)         ;; 한 줄(R7RS)
(eof-object? x)     ;; EOF 객체인가?
```

```scheme
(display "이름? ")
(define name (read-line))
(display "안녕, ") (display name) (newline)
```

### 10.3 포트(port)

I/O 추상화. 입력 포트, 출력 포트가 있다.

```scheme
(current-output-port)
(current-input-port)
(current-error-port)
```

### 10.4 파일 입출력

```scheme
(define out (open-output-file "out.txt"))
(display "hello\n" out)
(close-output-port out)

(define in (open-input-file "out.txt"))
(read-line in)            ;; ⇒ "hello"
(close-input-port in)
```

#### `with-output-to-file`

자동 닫기:

```scheme
(with-output-to-file "out.txt"
  (lambda ()
    (display "안녕\n")
    (display "세상\n")))
```

#### `call-with-input-file` / `call-with-output-file`

```scheme
(call-with-output-file "data.txt"
  (lambda (p)
    (write '(1 2 3 4 5) p)
    (newline p)))

(call-with-input-file "data.txt"
  (lambda (p)
    (read p)))                ;; ⇒ (1 2 3 4 5)
```

### 10.5 문자열 포트

문자열을 마치 파일처럼.

```scheme
(define out (open-output-string))
(display "hi " out)
(display 42 out)
(get-output-string out)       ;; ⇒ "hi 42"

(define in (open-input-string "(1 2 3)"))
(read in)                     ;; ⇒ (1 2 3)
```

### 10.6 형식화된 출력

R7RS-small에는 `printf`가 없다. 직접 만들거나 SRFI-28 `format`을 쓴다.

```scheme
;; 미니 format (간단 버전)
(define (myformat fmt . args)
  (let ((p (open-output-string)))
    (let loop ((i 0) (args args))
      (cond ((>= i (string-length fmt))
             (get-output-string p))
            ((and (char=? (string-ref fmt i) #\~)
                  (< (+ i 1) (string-length fmt)))
             (case (string-ref fmt (+ i 1))
               ((#\a) (display (car args) p)
                      (loop (+ i 2) (cdr args)))
               ((#\s) (write (car args) p)
                      (loop (+ i 2) (cdr args)))
               ((#\%) (newline p)
                      (loop (+ i 2) args))
               (else  (write-char (string-ref fmt i) p)
                      (loop (+ i 1) args))))
            (else
             (write-char (string-ref fmt i) p)
             (loop (+ i 1) args))))))

(myformat "안녕 ~a, 너의 점수는 ~a다.~%" "철수" 95)
;; ⇒ "안녕 철수, 너의 점수는 95다.\n"
```

### 10.7 EOF 처리

```scheme
(define (read-all-lines port)
  (let loop ((lines '()))
    (let ((line (read-line port)))
      (if (eof-object? line)
          (reverse lines)
          (loop (cons line lines))))))

(call-with-input-file "out.txt"
  read-all-lines)
;; ⇒ ("hello")
```

### 10.8 실전 — 단어 빈도 카운터(파일 입력)

```scheme
(define (word-count path)
  (define table (make-hash-table))   ; 24장 참고 — 처리계 의존
  (define (add! w)
    (hash-table-update! table w
      (lambda (n) (+ n 1)) 0))
  (call-with-input-file path
    (lambda (p)
      (let loop ()
        (let ((line (read-line p)))
          (unless (eof-object? line)
            (for-each add! (string-split line #\ ))
            (loop))))))
  (hash-table->alist table))
```

(처리계에 따라 `make-hash-table` 이름이 다르다 — `make-eqv-hashtable`(R6RS),
`make-equal-hash-table`(Racket) 등. 24장에서 이식 가능 버전을 다룬다.)

### 10.9 연습문제

1. 표준 입력에서 정수 한 줄을 읽어 절댓값을 출력하는 프로그램.
2. 텍스트 파일의 줄 수, 단어 수, 글자 수를 출력하는 미니 `wc`.
3. 사용자에게 숫자 5개를 묻고 평균을 출력.
4. 두 파일을 받아 *공통 줄*을 출력하는 프로그램 (set 자료구조 없이).

\newpage
# 2부 고급 문법

\newpage

## 11장 고차 함수와 함수형 패턴

### 11.1 고차 함수란

*함수를 인자로 받거나 함수를 결과로 돌려주는 함수*가 고차 함수다.
Scheme은 절차가 일급 시민(first-class)이므로 자연스럽게 고차 함수가 풍부하다.

```scheme
(define (apply-twice f x) (f (f x)))
(apply-twice (lambda (x) (+ x 1)) 5)   ;; ⇒ 7
```

### 11.2 핵심 사총사: `map`, `filter`, `fold-left`, `fold-right`

이 네 패턴은 *명령형 반복문 90%를 대체*한다.

#### `map`

```scheme
(map (lambda (x) (* x x)) '(1 2 3 4))   ;; ⇒ (1 4 9 16)
(map + '(1 2 3) '(10 20 30))            ;; ⇒ (11 22 33)
```

여러 리스트를 받으면 동일 인덱스 원소를 동시에 적용.

#### `filter` (R7RS-large / SRFI-1)

R7RS-small에는 없다. 직접 구현:

```scheme
(define (filter pred xs)
  (cond ((null? xs) '())
        ((pred (car xs))
         (cons (car xs) (filter pred (cdr xs))))
        (else (filter pred (cdr xs)))))

(filter odd? '(1 2 3 4 5))     ;; ⇒ (1 3 5)
(filter (lambda (x) (> x 3)) '(1 5 2 7))   ;; ⇒ (5 7)
```

#### `fold-left` / `fold-right`

```scheme
(define (fold-left f init xs)
  (if (null? xs) init
      (fold-left f (f init (car xs)) (cdr xs))))

(define (fold-right f init xs)
  (if (null? xs) init
      (f (car xs) (fold-right f init (cdr xs)))))

(fold-left + 0 '(1 2 3 4 5))       ;; ⇒ 15
(fold-left cons '() '(1 2 3))      ;; ⇒ (((() . 1) . 2) . 3)
(fold-right cons '() '(1 2 3))     ;; ⇒ (1 2 3)
(fold-right + 0 '(1 2 3 4 5))      ;; ⇒ 15
(fold-left max 0 '(3 1 4 1 5 9 2)) ;; ⇒ 9
```

`fold-left`는 꼬리 재귀로 효율적, `fold-right`는 자연스러운 재귀 형태.

### 11.3 `map`/`fold`로 다시 표현하기

```scheme
;; 합
(define (sum xs) (fold-left + 0 xs))

;; 곱
(define (product xs) (fold-left * 1 xs))

;; 길이
(define (length* xs) (fold-left (lambda (n _) (+ n 1)) 0 xs))

;; 뒤집기
(define (reverse* xs) (fold-left (lambda (acc x) (cons x acc)) '() xs))

;; 평탄화 한 단계
(define (concat xss) (fold-right append '() xss))

;; 매핑도 fold로
(define (my-map f xs)
  (fold-right (lambda (x acc) (cons (f x) acc)) '() xs))
```

이렇게 `fold`는 *모든 리스트 처리의 모(母) 패턴*이다.

### 11.4 부분 적용과 커리화

```scheme
;; 부분 적용
(define (partial f . args)
  (lambda more-args (apply f (append args more-args))))

(define add5 (partial + 5))
(add5 10)                         ;; ⇒ 15

;; 커리화 (2-인자 → 1-인자 두 번)
(define (curry2 f) (lambda (x) (lambda (y) (f x y))))

(((curry2 +) 3) 4)                ;; ⇒ 7
```

### 11.5 함수 합성

```scheme
(define (compose . fns)
  (cond ((null? fns) (lambda (x) x))
        ((null? (cdr fns)) (car fns))
        (else
         (let ((f (car fns)) (g (apply compose (cdr fns))))
           (lambda args (f (apply g args)))))))

(define inc (lambda (x) (+ x 1)))
(define dbl (lambda (x) (* x 2)))
((compose dbl inc inc) 3)         ;; ⇒ 10
```

### 11.6 동등성 일반화 — `eq?`/`eqv?`/`equal?` 와 비교 함수

정렬·검색 함수에 비교 함수를 인자로 넘기는 패턴은 매우 흔하다.

```scheme
(define (max-by key xs)
  (let loop ((best (car xs)) (rest (cdr xs)))
    (cond ((null? rest) best)
          ((> (key (car rest)) (key best))
           (loop (car rest) (cdr rest)))
          (else (loop best (cdr rest))))))

(max-by string-length '("a" "abc" "ab"))   ;; ⇒ "abc"
```

### 11.7 함수형 자료 변환 파이프라인

```scheme
;; 학생 점수 alist에서 평균 80 이상만 골라 이름 리스트
(define students
  '((철수 . 75) (영희 . 92) (민수 . 87) (지영 . 60)))

(map car
  (filter (lambda (p) (>= (cdr p) 80)) students))
;; ⇒ (영희 민수)
```

### 11.8 모나드(Maybe) 흉내내기

오류를 *값*으로 다루는 함수형 관용구.

```scheme
(define (just x) (cons 'just x))
(define (nothing) '(nothing))
(define (just? m) (eq? (car m) 'just))
(define (from-just m) (cdr m))

(define (>>= m f)
  (if (just? m) (f (from-just m)) m))

;; 안전한 나눗셈 체인
(define (safe/ a b)
  (if (zero? b) (nothing) (just (/ a b))))

(>>= (safe/ 10 2) (lambda (x)
  (>>= (safe/ x 5) (lambda (y)
    (just y)))))
;; ⇒ (just . 1)

(>>= (safe/ 10 0) (lambda (x)
  (>>= (safe/ x 5) (lambda (y)
    (just y)))))
;; ⇒ (nothing)
```

### 11.9 연습문제

1. `(any pred xs)` — xs 중 하나라도 pred가 참이면 #t.
   `every`도 작성하라. 둘 다 `fold`로 표현해 보라.
2. `(zip xs ys)` — 두 리스트를 페어 리스트로. 길이 다르면 짧은 쪽 기준.
3. `(group-by key xs)` — xs를 key 함수 결과로 묶어 alist를 만든다.
4. `(memoize f)` — 일반적 1-인자 함수 메모이제이션.

\newpage

## 12장 클로저와 상태 캡슐화

### 12.1 클로저의 정의

**클로저(closure)** = 절차 + 그 절차가 정의된 *환경*.

```scheme
(define (make-adder n)
  (lambda (x) (+ x n)))

(define add5 (make-adder 5))
(add5 10)                ;; ⇒ 15
(add5 20)                ;; ⇒ 25
```

`add5`는 `(lambda (x) (+ x n))`이라는 코드와 *n=5인 환경*을 함께 들고 다닌다.

### 12.2 가변 상태

`set!`을 클로저 안에 두면 *비공개 상태*가 된다.

```scheme
(define (make-counter)
  (let ((n 0))
    (lambda ()
      (set! n (+ n 1))
      n)))

(define c (make-counter))
(c) (c) (c)              ;; ⇒ 1, 2, 3
```

`n`은 외부에서 접근 불가 — 객체지향에서 *private 필드*에 해당.

### 12.3 메시지 디스패치 = 객체

```scheme
(define (make-account balance)
  (define (deposit amt) (set! balance (+ balance amt)) balance)
  (define (withdraw amt)
    (if (> amt balance)
        'insufficient
        (begin (set! balance (- balance amt)) balance)))
  (define (balance-of) balance)
  (lambda (msg . args)
    (case msg
      ((deposit) (apply deposit args))
      ((withdraw) (apply withdraw args))
      ((balance) (balance-of))
      (else (error "unknown message" msg)))))

(define a (make-account 100))
(a 'deposit 50)         ;; ⇒ 150
(a 'withdraw 70)        ;; ⇒ 80
(a 'balance)            ;; ⇒ 80
```

### 12.4 알리스 외 — alist, vector를 이용한 객체

```scheme
(define (make-point x y)
  (list (cons 'x x) (cons 'y y)))

(define (get o k) (cdr (assq k o)))

(let ((p (make-point 3 4)))
  (sqrt (+ (* (get p 'x) (get p 'x))
           (* (get p 'y) (get p 'y)))))
;; ⇒ 5.0
```

### 12.5 메모이제이션

```scheme
(define (memoize f)
  (let ((cache '()))
    (lambda (x)
      (cond ((assoc x cache) => cdr)
            (else
             (let ((r (f x)))
               (set! cache (cons (cons x r) cache))
               r))))))

(define slow-square
  (lambda (x) (display "*") (* x x)))

(define fast-square (memoize slow-square))

(fast-square 5)   ;; → *  ⇒ 25
(fast-square 5)   ;; ⇒ 25 (출력 없음 — 캐시 적중)
```

### 12.6 클로저로 만드는 *값 객체*

```scheme
(define (make-stack)
  (let ((items '()))
    (define (push! x) (set! items (cons x items)))
    (define (pop!)
      (if (null? items) (error "empty")
          (let ((x (car items)))
            (set! items (cdr items))
            x)))
    (define (top) (car items))
    (define (empty?) (null? items))
    (lambda (m . a)
      (case m
        ((push) (push! (car a)))
        ((pop) (pop!))
        ((top) (top))
        ((empty?) (empty?))))))

(define s (make-stack))
(s 'push 1) (s 'push 2) (s 'push 3)
(s 'pop)             ;; ⇒ 3
(s 'top)             ;; ⇒ 2
(s 'empty?)          ;; ⇒ #f
```

### 12.7 자주 나오는 함정 — 공유된 상태

```scheme
;; 잘못된 예 — 모든 클로저가 같은 i를 본다
(define fns
  (let loop ((i 0) (acc '()))
    (if (= i 3) (reverse acc)
        (loop (+ i 1)
              (cons (lambda () i) acc)))))   ; ← 변수 i 공유 X
;; (각 반복의 i는 새 바인딩이라 OK)
```

`let`/`do`는 매 반복 *새 바인딩*을 만들기 때문에 안전하다.
하지만 단일 변수에 `set!`로 갱신하는 경우엔 문제가 된다.

```scheme
;; 함정
(define fns
  (let ((i 0) (acc '()))
    (let loop ()
      (if (= i 3) (reverse acc)
          (begin
            (set! acc (cons (lambda () i) acc))
            (set! i (+ i 1))
            (loop))))))

((car fns))  ;; ⇒ 3   ; 모두 마지막 i를 본다
```

해결: 람다를 만들 때 *값을 즉시 캡처*.

```scheme
(set! acc (cons (let ((j i)) (lambda () j)) acc))
```

### 12.8 연습문제

1. `make-bank-account`에 password 인자를 추가해, 잘못된 비번이면
   `'wrong-password`를 돌려주도록 확장하라.
2. `make-cycler`: 인자로 받은 리스트를 호출할 때마다 한 원소씩 순환해 돌려준다.
3. 함수 호출 횟수를 세는 데코레이터 `(count-calls f)`를 작성하라.
   `((count-calls f) 'count)`로 횟수 조회.
4. *순수* 함수형 카운터를 만들어 보라. (힌트: 다음 카운터를 반환)

\newpage

## 13장 꼬리호출과 누적자 패턴

### 13.1 꼬리 위치(tail position)

식이 *그 절차의 마지막에 평가되어 그 값이 그대로 반환*되면 그 식은 꼬리 위치에 있다.

```scheme
(define (f x)
  (if (zero? x) 'done       ; 'done 은 꼬리 위치
      (g (- x 1))))         ; (g ...) 은 꼬리 위치

(define (h x)
  (+ 1 (f x)))              ; (f x) 는 꼬리 위치 아님 — +1 이 남음
```

R7RS는 모든 처리계가 꼬리 호출을 *상수 스택*으로 처리하도록 강제한다.

### 13.2 누적자 패턴 변환

자연스러운 재귀를 누적자 형태로 바꾸는 일반적 절차:

#### 단계 1 — 일반 재귀

```scheme
(define (sum xs)
  (if (null? xs) 0
      (+ (car xs) (sum (cdr xs)))))
```

#### 단계 2 — 누적자 추가

```scheme
(define (sum-iter xs acc)
  (if (null? xs) acc
      (sum-iter (cdr xs) (+ acc (car xs)))))

(define (sum xs) (sum-iter xs 0))
```

#### 단계 3 — 명명된 let으로 정리

```scheme
(define (sum xs)
  (let loop ((xs xs) (acc 0))
    (if (null? xs) acc
        (loop (cdr xs) (+ acc (car xs))))))
```

### 13.3 피보나치 — 트리 재귀에서 선형으로

```scheme
;; O(2^n)
(define (fib-tree n)
  (if (< n 2) n
      (+ (fib-tree (- n 1)) (fib-tree (- n 2)))))

;; O(n) 누적자
(define (fib n)
  (let loop ((i 0) (a 0) (b 1))
    (if (= i n) a
        (loop (+ i 1) b (+ a b)))))

(fib 30)   ;; ⇒ 832040
(fib 100)  ;; ⇒ 354224848179261915075
```

(Scheme 정수는 임의 정밀도이므로 `fib 100`도 정확히 계산된다.)

### 13.4 두 누적자가 필요할 때 — 평균

```scheme
(define (mean xs)
  (let loop ((xs xs) (sum 0) (n 0))
    (if (null? xs)
        (/ sum n)
        (loop (cdr xs) (+ sum (car xs)) (+ n 1)))))

(mean '(1 2 3 4 5))   ;; ⇒ 3
```

### 13.5 *연속 전달 스타일*(CPS)로 비꼬리 변환

`(+ 1 (f x))` 같은 식도 CPS로 다시 쓰면 꼬리 호출만 남는다.

```scheme
;; 일반: 비꼬리
(define (length* xs)
  (if (null? xs) 0
      (+ 1 (length* (cdr xs)))))

;; CPS: 다음에 할 일을 k에 담아 넘긴다
(define (length-cps xs k)
  (if (null? xs) (k 0)
      (length-cps (cdr xs)
                  (lambda (n) (k (+ n 1))))))

(length-cps '(a b c d) (lambda (x) x))   ;; ⇒ 4
```

CPS는 14장의 `call/cc`를 이해하는 길잡이가 된다.

### 13.6 상호 재귀와 꼬리 호출

```scheme
(define (even? n) (if (zero? n) #t (odd?  (- n 1))))
(define (odd?  n) (if (zero? n) #f (even? (- n 1))))

(even? 1000000)   ;; ⇒ #t   ; 처리계가 꼬리호출 최적화하므로 OK
```

### 13.7 실전 — 리스트 평탄화

```scheme
;; 자연 재귀
(define (flatten t)
  (cond ((null? t) '())
        ((pair? (car t))
         (append (flatten (car t)) (flatten (cdr t))))
        (else (cons (car t) (flatten (cdr t))))))

(flatten '(1 (2 (3 4) 5) (6 (7))))   ;; ⇒ (1 2 3 4 5 6 7)

;; 누적자
(define (flatten* t)
  (let loop ((t t) (acc '()))
    (cond ((null? t) acc)
          ((pair? t)
           (loop (car t) (loop (cdr t) acc)))
          (else (cons t acc)))))

(flatten* '(1 (2 (3 4) 5) (6 (7))))   ;; ⇒ (1 2 3 4 5 6 7)
```

### 13.8 연습문제

1. `factorial`을 일반 재귀와 누적자 두 버전으로 작성하고
   (`fact 100000`) 둘의 동작 차이를 관찰하라.
2. `(reverse-iter xs)`을 `fold-left`로 한 줄에 작성하라.
3. CPS로 `factorial`을 작성하라.
4. 꼬리 위치인지 아닌지 다음 식들을 분류하라:
   - `(if a b c)`의 b — 꼬리?
   - `(let ((x e)) body)`의 body — 꼬리?
   - `(begin a b c)`의 a — 꼬리?
   - `(cond (a b) (else c))`의 b — 꼬리?

\newpage

## 14장 연속과 `call/cc`

### 14.1 연속이란

*어떤 식의 연속(continuation)*은 그 식이 평가된 뒤 *남은 모든 일*이다.
다음 코드에서:

```scheme
(+ 1 (f x))
```

`(f x)`의 연속은 "결과에 1을 더하고, 그 값을 둘러싼 식에 돌려준다"이다.

### 14.2 `call-with-current-continuation` (`call/cc`)

`(call/cc proc)`는 *현재의 연속*을 `proc`에 일급 함수로 넘긴다.

```scheme
(+ 1 (call/cc
        (lambda (k)
          (+ 2 (k 10)))))
;; ⇒ 11   ; (+ 2 ...) 안에서 k(10)이 호출되면
;;          k는 "이 자리의 + 1 ..." 으로 점프한다.
```

`(k 10)`은 *그 자리의 모든 작업을 버리고*
저장해 둔 연속(여기선 "결과에 1을 더한 뒤 반환")으로 점프한다.

### 14.3 `call/cc`로 만드는 조기 탈출

```scheme
(define (find-first pred xs)
  (call/cc
   (lambda (return)
     (for-each (lambda (x)
                 (when (pred x) (return x)))
               xs)
     #f)))

(find-first odd? '(2 4 6 7 8))   ;; ⇒ 7
(find-first odd? '(2 4 6 8))     ;; ⇒ #f
```

이는 다른 언어의 `return` 키워드와 같은 역할이다.

### 14.4 예외 처리(R7RS의 `guard` 이전 시대)

```scheme
(define *handler* #f)

(define (try thunk handler)
  (call/cc (lambda (k)
    (let ((old *handler*))
      (set! *handler*
        (lambda (e)
          (set! *handler* old)
          (k (handler e))))
      (let ((r (thunk)))
        (set! *handler* old)
        r)))))

(define (raise* e) (*handler* e))

(try
  (lambda ()
    (raise* 'boom)
    'never)
  (lambda (e) (list 'caught e)))
;; ⇒ (caught boom)
```

(실전에서는 18장의 `guard`/`raise`를 쓰자.)

### 14.5 코루틴

`call/cc`로 두 코루틴이 서로의 연속을 주고받게 만든다.

```scheme
(define (make-generator producer)
  (define resume-producer #f)
  (define resume-consumer #f)
  (define (yield v)
    (call/cc (lambda (k)
      (set! resume-producer k)
      (resume-consumer v))))
  (lambda ()
    (call/cc (lambda (k)
      (set! resume-consumer k)
      (if resume-producer
          (resume-producer #f)
          (begin (producer yield) (resume-consumer 'done)))))))

(define gen
  (make-generator
   (lambda (yield)
     (yield 1)
     (yield 2)
     (yield 3))))

(gen)   ;; ⇒ 1
(gen)   ;; ⇒ 2
(gen)   ;; ⇒ 3
```

### 14.6 다중 호출 가능성 — 시간 여행

`call/cc`로 잡은 연속은 *여러 번* 호출할 수 있다.
이 성질이 Scheme의 연속을 "first-class continuation"이라 부르게 한다.

```scheme
(define saved #f)

(define (test)
  (display "start ")
  (let ((x (call/cc (lambda (k) (set! saved k) 0))))
    (display x) (display " ")
    x))

(test)        ;; → start 0  ⇒ 0
(saved 10)    ;; → 10        ⇒ 10
(saved 20)    ;; → 20        ⇒ 20
```

`saved`는 *그 시점의 평가 자리*를 들고 있어, 호출할 때마다 그 자리부터 다시 진행한다.

### 14.7 비결정적 검색 — `amb`

```scheme
(define fail #f)

(define (init-amb)
  (set! fail (lambda () (error "no more choices"))))

(define-syntax amb
  (syntax-rules ()
    ((_) (fail))
    ((_ a b ...)
     (let ((prev fail))
       (call/cc (lambda (k)
         (set! fail (lambda () (set! fail prev) (k (amb b ...))))
         a))))))

(define (assert! x) (unless x (fail)))

(init-amb)

;; 피타고라스 삼중쌍
(let ((a (amb 1 2 3 4 5))
      (b (amb 1 2 3 4 5))
      (c (amb 1 2 3 4 5)))
  (assert! (<= a b c))
  (assert! (= (+ (* a a) (* b b)) (* c c)))
  (list a b c))
;; ⇒ (3 4 5)
```

### 14.8 주의

- 연속은 *전체* 평가 상태를 잡으므로, 큰 동적 문맥이라면 메모리 비용이 크다.
- `dynamic-wind`(보호자/마무리)와 상호작용에 주의.
- 처리계 마다 비용이 다르다 — Chez와 Racket은 매우 빠르지만, 다른 곳에서는 무겁다.

### 14.9 연습문제

1. `call/cc`로 `break` 흉내 — 리스트를 순회하다 어떤 조건에서 중단.
2. `call/cc`로 `(any pred xs)`를 한 번의 `for-each`로 작성.
3. 위 amb 매크로를 써 *N-퀸* 문제(작은 N)를 풀어보라.
4. 한 번 호출되면 *영원히 다른 연산을 막는* 일회성 토큰을 `call/cc`로 만들어 보라.

\newpage

## 15장 위생 매크로 `syntax-rules`

### 15.1 매크로란

매크로는 *컴파일 시점에* 코드를 다른 코드로 바꾸는 규칙이다.
함수가 *값*을 다룬다면, 매크로는 *문법*을 다룬다.

`(when c body...)`은 매크로다 — 인자가 평가되기 전에
`(if c (begin body...))`로 *치환*된 뒤 평가된다.

### 15.2 `syntax-rules` 기본형

```scheme
(define-syntax 매크로이름
  (syntax-rules (literal-id ...)
    (패턴1 템플릿1)
    (패턴2 템플릿2)
    ...))
```

### 15.3 가장 단순한 매크로

```scheme
(define-syntax my-when
  (syntax-rules ()
    ((_ test body ...)
     (if test (begin body ...)))))

(my-when (> 3 1) (display "yes") (newline))
;; → yes
```

`...`은 *0개 이상 반복*을 뜻한다.

### 15.4 `unless`

```scheme
(define-syntax my-unless
  (syntax-rules ()
    ((_ test body ...)
     (if (not test) (begin body ...)))))
```

### 15.5 `swap!`

```scheme
(define-syntax swap!
  (syntax-rules ()
    ((_ a b)
     (let ((tmp a))
       (set! a b)
       (set! b tmp)))))

(define x 1) (define y 2)
(swap! x y)
(list x y)            ;; ⇒ (2 1)
```

이게 단순 *텍스트 치환*이라면 위험할 수 있다 — `(swap! tmp x)`처럼
이름이 충돌하면 어떻게 되나? `syntax-rules`는 *위생적*이다 —
매크로 내부의 `tmp`는 자동으로 **신선한 이름**으로 바뀐다. 충돌하지 않는다.

```scheme
(define tmp 100)
(define a 1) (define b 2)
(swap! tmp a)
(list tmp a)         ;; ⇒ (1 100)   ; 매크로 내부 tmp와 충돌 X
```

### 15.6 `or`/`and` 직접 만들기

표준 `or`/`and` 자체가 매크로다(특수형 아님).

```scheme
(define-syntax my-or
  (syntax-rules ()
    ((_) #f)
    ((_ e) e)
    ((_ e1 e2 ...)
     (let ((x e1)) (if x x (my-or e2 ...))))))

(define-syntax my-and
  (syntax-rules ()
    ((_) #t)
    ((_ e) e)
    ((_ e1 e2 ...)
     (if e1 (my-and e2 ...) #f))))

(my-or #f #f 'yes #f)     ;; ⇒ yes
(my-and 1 2 3)            ;; ⇒ 3
(my-and 1 #f 3)           ;; ⇒ #f
```

### 15.7 패턴의 리터럴

```scheme
(define-syntax my-cond
  (syntax-rules (else)
    ((_ (else e ...)) (begin e ...))
    ((_ (c e ...) rest ...)
     (if c (begin e ...) (my-cond rest ...)))
    ((_) (begin))))

(my-cond
 ((> 3 5) 'a)
 ((= 1 1) 'b)
 (else    'c))
;; ⇒ b
```

`else`는 리터럴로 선언했으므로 *변수가 아니라 키워드*로 매칭된다.

### 15.8 `let`을 매크로로 정의

```scheme
(define-syntax my-let
  (syntax-rules ()
    ((_ ((x v) ...) body ...)
     ((lambda (x ...) body ...) v ...))))

(my-let ((a 1) (b 2)) (+ a b))   ;; ⇒ 3
```

`let`이 람다의 *문법 설탕*이라는 점이 그대로 드러난다.

### 15.9 매크로 안에 매크로

```scheme
(define-syntax for
  (syntax-rules (in)
    ((_ x in xs body ...)
     (for-each (lambda (x) body ...) xs))))

(for x in '(1 2 3)
  (display x) (display " "))
;; → 1 2 3
```

### 15.10 흔한 함정

#### 다중 평가

```scheme
;; 잘못된 정의 — e가 두 번 평가됨!
(define-syntax square-bad
  (syntax-rules ()
    ((_ e) (* e e))))

(square-bad (begin (display "*") 5))   ;; → ** ⇒ 25
```

해결: 한 번 묶어 `let`에 담는다.

```scheme
(define-syntax square-good
  (syntax-rules ()
    ((_ e) (let ((x e)) (* x x)))))
```

#### 변수 캡처

`syntax-rules`는 위생적이라 일반적인 캡처는 일어나지 않는다.
하지만 *의도적 캡처*(이름이 바깥과 같아야 함)는 16장의 `syntax-case`로.

### 15.11 연습문제

1. `(while c body...)` 매크로 — 조건이 참인 동안 body를 반복.
2. `(repeat n body...)` 매크로 — n번 반복.
3. `(begin0 e1 e2 ...)` — e1을 모두 평가하지만 e1의 값을 반환.
4. `(cond->>` ... `)` — 클로저 식 파이프라인. (도전과제)

\newpage

## 16장 저수준 매크로 `syntax-case`

### 16.1 왜 `syntax-case`인가

`syntax-rules`는 충분히 강력하지만 *순수 패턴*만 다룬다.
*컴파일 시점의 임의 계산*이 필요하면 `syntax-case`를 쓴다.
R6RS와 Racket(`(require (for-syntax racket/base))` 등)에서 표준이다.

### 16.2 첫 예

```scheme
(define-syntax my-when
  (lambda (stx)
    (syntax-case stx ()
      ((_ c body ...)
       #'(if c (begin body ...))))))
```

- `lambda` 안에서 *문법 객체* `stx`를 받는다.
- `syntax-case`로 패턴 매칭.
- `#'(...)`은 *템플릿 만들기*.

### 16.3 컴파일 시 계산

```scheme
(define-syntax precomputed-square
  (lambda (stx)
    (syntax-case stx ()
      ((_ n)
       (let ((v (* (syntax->datum #'n) (syntax->datum #'n))))
         (datum->syntax #'n v))))))

(precomputed-square 7)   ;; ⇒ 49 (컴파일 시 49로 치환)
```

### 16.4 의도적 캡처 — `datum->syntax`

```scheme
(define-syntax aif
  (lambda (stx)
    (syntax-case stx ()
      ((_ c t e)
       (with-syntax ((it (datum->syntax #'c 'it)))
         #'(let ((it c))
             (if it t e)))))))

(aif (assq 'b '((a . 1) (b . 2))) (cdr it) 'no)
;; ⇒ 2
```

`it`이 보통 위생적으로 신선해질 텐데, `datum->syntax`로
사용처(`#'c`)와 같은 어휘 문맥에 묶어 *의도적 캡처*를 만든다.

### 16.5 가드 — 패턴 부가 조건

```scheme
(define-syntax positive-only
  (lambda (stx)
    (syntax-case stx ()
      ((_ n)
       (positive? (syntax->datum #'n))
       #'n)
      ((_ _) #'(error "not positive")))))

(positive-only 3)        ;; ⇒ 3
(positive-only -1)       ;; → 컴파일 오류 또는 런타임 에러
```

(Scheme R7RS-small은 `syntax-case`를 의무로 두지 않는다 — 처리계 의존. 핵심은
*매크로 시스템이 더 깊은 충(저수준)을 제공한다*는 사실 자체다.)

### 16.6 `er-macro-transformer` (Chicken/Chibi 등)

또 다른 인기 있는 저수준 인터페이스. 이 책은 가독성을 위해 자세히 다루지 않지만
*명시적 이름 재명명*(explicit renaming)을 통해 위생을 직접 통제한다.

### 16.7 매크로 전개 디버깅

Racket: `expand` 또는 macro stepper. Chez: `(expand 'expr)`.

```scheme
(expand '(my-when (= 1 1) (display "ok")))
;; → (if (= 1 1) (begin (display "ok")))
```

### 16.8 연습문제

1. `bind-set!` — `(bind-set! ((a 1) (b 2)) ...)` 본문 안에서 a, b가 set!로 갱신 가능.
2. `let1` — `(let1 x v body...)` 단일 바인딩 let.
3. `defstruct` — 간단한 레코드 매크로(필드 접근자/생성자 자동 생성).
4. `aif`를 `syntax-rules`로는 정의할 수 없는 이유를 한 문단으로 설명하라.

\newpage

## 17장 지연 평가와 스트림

### 17.1 `delay` / `force`

```scheme
(define p (delay (begin (display "계산!") (* 6 7))))

p                ;; ⇒ #<promise>
(force p)        ;; → 계산! ⇒ 42
(force p)        ;; ⇒ 42        (다시 출력하지 않음 — 메모이즈)
```

`delay`는 식을 *지연* 시키고, `force`는 첫 호출 때 평가하여 결과를 캐싱한다.

### 17.2 무한 스트림

```scheme
;; 스트림 = (헤드 . 지연된 꼬리)
(define-syntax cons-stream
  (syntax-rules ()
    ((_ a b) (cons a (delay b)))))

(define (stream-car s) (car s))
(define (stream-cdr s) (force (cdr s)))

(define (integers-from n)
  (cons-stream n (integers-from (+ n 1))))

(define ints (integers-from 1))
(stream-car ints)                            ;; ⇒ 1
(stream-car (stream-cdr ints))               ;; ⇒ 2
(stream-car (stream-cdr (stream-cdr ints)))  ;; ⇒ 3
```

### 17.3 스트림 절차들

```scheme
(define (stream-take s n)
  (if (zero? n) '()
      (cons (stream-car s) (stream-take (stream-cdr s) (- n 1)))))

(define (stream-map f s)
  (cons-stream (f (stream-car s))
               (stream-map f (stream-cdr s))))

(define (stream-filter p s)
  (cond ((p (stream-car s))
         (cons-stream (stream-car s) (stream-filter p (stream-cdr s))))
        (else (stream-filter p (stream-cdr s)))))

(stream-take ints 10)                  ;; ⇒ (1 2 3 4 5 6 7 8 9 10)
(stream-take (stream-map (lambda (x) (* x x)) ints) 5)
;; ⇒ (1 4 9 16 25)
```

### 17.4 시브로 만드는 무한 소수 스트림

```scheme
(define (sieve s)
  (cons-stream
    (stream-car s)
    (sieve (stream-filter
            (lambda (x) (not (zero? (modulo x (stream-car s)))))
            (stream-cdr s)))))

(define primes (sieve (integers-from 2)))

(stream-take primes 10)
;; ⇒ (2 3 5 7 11 13 17 19 23 29)
```

### 17.5 자기 참조 스트림

```scheme
(define ones (cons-stream 1 ones))
(stream-take ones 5)              ;; ⇒ (1 1 1 1 1)

(define (add-streams s t)
  (cons-stream (+ (stream-car s) (stream-car t))
               (add-streams (stream-cdr s) (stream-cdr t))))

(define nats (cons-stream 0 (add-streams ones nats)))
(stream-take nats 10)             ;; ⇒ (0 1 2 3 4 5 6 7 8 9)

(define fibs
  (cons-stream 0
    (cons-stream 1
      (add-streams fibs (stream-cdr fibs)))))

(stream-take fibs 12)
;; ⇒ (0 1 1 2 3 5 8 13 21 34 55 89)
```

이 우아함이 지연 평가가 주는 선물이다.

### 17.6 연습문제

1. `stream-ref s n` — n번째 원소.
2. 자연수의 제곱 스트림.
3. *해밍 수*(2,3,5만 소인수) 스트림.
4. 임의의 두 스트림을 인터리브하는 `stream-interleave`.

\newpage

## 18장 예외 처리 `guard` / `raise`

### 18.1 `raise` / `error`

```scheme
(raise 'my-error)               ;; 임의 객체를 던질 수 있다
(error "잘못된 인자" 42)         ;; 사람이 읽는 메시지 + 데이터
```

R7RS의 `error`는 메시지와 함께 *오류 객체*를 던진다.

### 18.2 `guard`

```scheme
(guard (e (조건1 처리1)
          (조건2 처리2)
          ...)
  본문)
```

`e`는 잡힌 값. 조건은 술어식.

```scheme
(guard (e ((symbol? e) (list 'sym e))
          ((string? e) (list 'msg e))
          (else (list 'other e)))
  (raise 'oops))
;; ⇒ (sym oops)

(guard (e ((string? e) (list 'msg e))
          (else (raise e)))     ; 다시 던짐
  (raise 'unhandled))
;; → 처리 안 됨
```

### 18.3 `error-object?`와 동반 절차

```scheme
(guard (e ((error-object? e)
           (list 'err
                 (error-object-message e)
                 (error-object-irritants e))))
  (error "잘못된 입력" 1 2 3))
;; ⇒ (err "잘못된 입력" (1 2 3))
```

### 18.4 with-exception-handler

저수준 인터페이스.

```scheme
(with-exception-handler
  (lambda (e) (display "잡힘: ") (display e) (newline))
  (lambda ()
    (raise 'bad)))
;; → 잡힘: bad
```

`raise`로 던진 예외는 *재시작 불가능*(처리기 반환 시 처리계 정의 행동).
`raise-continuable`로 던지면 처리기 반환 값이 `raise-continuable`의 결과가 된다.

### 18.5 finally 흉내내기

R7RS-small에는 `finally`가 없다. `dynamic-wind`로 만든다.

```scheme
(define (with-cleanup body cleanup)
  (dynamic-wind
    (lambda () #f)         ; before
    body                   ; body
    cleanup))              ; after — 정상/예외 모두 호출

(with-cleanup
  (lambda () (display "작업\n") 42)
  (lambda () (display "정리\n")))
;; → 작업
;;   정리
;; ⇒ 42
```

### 18.6 사용자 정의 예외 객체

```scheme
(define-record-type validation-error
  (make-validation-error field reason)
  validation-error?
  (field validation-error-field)
  (reason validation-error-reason))

(guard (e ((validation-error? e)
           (display "필드: ") (display (validation-error-field e))
           (newline)))
  (raise (make-validation-error 'email "형식 오류")))
```

### 18.7 연습문제

1. `safe-/` — 0으로 나누면 `'div-by-zero`를 돌려주는 안전한 나눗셈.
2. 예외 발생 위치와 횟수를 기록하는 로거를 `with-exception-handler`로.
3. `try-finally`를 매크로로 작성 — `(try ... finally cleanup)` 형태.
4. *체인된 예외*(원인 보존)를 모델링하라.

\newpage

## 19장 모듈과 라이브러리

### 19.1 R7RS `define-library`

```scheme
(define-library (my math)
  (export square cube)
  (import (scheme base))
  (begin
    (define (square x) (* x x))
    (define (cube x) (* x (square x)))))
```

다른 파일에서:

```scheme
(import (my math))
(square 5)    ;; ⇒ 25
```

### 19.2 라이브러리 이름 규칙

라이브러리 이름은 *심볼 리스트* — 디렉토리 경로처럼 쓴다.

```
(scheme base)         ; 표준 기본
(scheme write)        ; display/write
(scheme char)         ; 문자 절차
(scheme file)         ; 파일 I/O
(scheme read) (scheme load) ...
```

### 19.3 `import` 변형

```scheme
(import (only (scheme base) car cdr cons))
(import (except (scheme base) error))
(import (rename (my math) (square sq) (cube cb)))
(import (prefix (my math) m:))     ; m:square, m:cube
```

### 19.4 모듈 본문에서의 `cond-expand`

처리계별 분기.

```scheme
(define-library (compat)
  (export hash-table-make)
  (cond-expand
    (chibi
      (import (chibi hash-table))
      (begin (define (hash-table-make) (make-hash-table equal?))))
    (racket
      (import (only (racket base) make-hash))
      (begin (define (hash-table-make) (make-hash))))
    (else
      (begin (define (hash-table-make) (error "지원 안함"))))))
```

### 19.5 Racket의 `module` (참고)

```scheme
#lang racket
(module my-mod racket
  (provide square)
  (define (square x) (* x x)))
```

`require`로 가져옴: `(require (submod "." my-mod))`.

### 19.6 파일 분리 예시

`math.sld`:

```scheme
(define-library (my math)
  (export square cube)
  (import (scheme base))
  (include "math.scm"))
```

`math.scm`:

```scheme
(define (square x) (* x x))
(define (cube x) (* x (square x)))
```

`main.scm`:

```scheme
(import (scheme base) (scheme write) (my math))
(display (square 7)) (newline)
```

### 19.7 연습문제

1. `(my list)` 라이브러리에 `take`/`drop`/`zip`을 정의해 export 하라.
2. 처리계 분기 — `(cond-expand)`로 Racket과 Chez 모두에서 동작하는
   `current-time-ms` 절차를 작성하라.
3. 라이브러리 `(my types)` 안에서 정의된 *비공개* 헬퍼는
   외부에서 접근 가능한가? 실험으로 확인하라.

\newpage

## 20장 다중 값

### 20.1 `values` / `call-with-values`

여러 값을 한 번에 돌려주는 매커니즘.

```scheme
(values 1 2 3)
;; ⇒ 1, 2, 3 (출력 형식은 처리계 의존)

(call-with-values
  (lambda () (values 1 2 3))
  (lambda (a b c) (+ a b c)))
;; ⇒ 6
```

`call-with-values`는 *생성자*(thunk)와 *소비자*(절차)를 받아 다중 값을 흘려보낸다.

### 20.2 `let-values`

```scheme
(define (div-mod a b) (values (quotient a b) (remainder a b)))

(let-values (((q r) (div-mod 17 5)))
  (list q r))
;; ⇒ (3 2)
```

### 20.3 `define-values`

```scheme
(define-values (a b c) (values 1 2 3))
(list a b c)             ;; ⇒ (1 2 3)
```

### 20.4 실용 예 — min/max 동시에

```scheme
(define (min-max xs)
  (let loop ((xs (cdr xs)) (lo (car xs)) (hi (car xs)))
    (cond ((null? xs) (values lo hi))
          ((< (car xs) lo) (loop (cdr xs) (car xs) hi))
          ((> (car xs) hi) (loop (cdr xs) lo (car xs)))
          (else (loop (cdr xs) lo hi)))))

(let-values (((lo hi) (min-max '(3 1 4 1 5 9 2 6 5))))
  (list 'min lo 'max hi))
;; ⇒ (min 1 max 9)
```

### 20.5 다중 값 vs 리스트/페어

리스트 반환은 *값을 모아* 호출자가 분해한다.
다중 값은 *호출자가 받을 그릇을 정한다*.
효율과 의도 표현 모두에서 다중 값이 깔끔할 때가 많다.

```scheme
;; 리스트 방식
(define (div-mod-list a b) (list (quotient a b) (remainder a b)))
(define p (div-mod-list 17 5))
(list (car p) (cadr p))                ;; ⇒ (3 2)
```

### 20.6 연습문제

1. 리스트의 짝수 합과 홀수 합을 동시에 돌려주는 절차.
2. 두 정수의 *몫·나머지·gcd*를 한 번에.
3. 리스트의 *최솟값과 그 위치*를 다중 값으로.
4. `partition`을 다중 값으로 — `(values yes no)`.

\newpage
# 3부 자료 구조

\newpage

## 21장 페어와 리스트 깊이 보기

### 21.1 페어(pair)

페어는 Scheme의 가장 기본적인 합성 자료 — *cons cell*이라고도 한다.

```scheme
(cons 1 2)           ;; ⇒ (1 . 2)
(car (cons 1 2))     ;; ⇒ 1
(cdr (cons 1 2))     ;; ⇒ 2
(pair? (cons 1 2))   ;; ⇒ #t
```

내부적으로 페어는 두 칸을 가진 작은 박스다.

```
+---+---+
| 1 | 2 |
+---+---+
  ^   ^
 car cdr
```

### 21.2 리스트는 페어의 사슬

```
'(1 2 3) = (cons 1 (cons 2 (cons 3 '())))
```

```scheme
(cons 1 (cons 2 (cons 3 '())))   ;; ⇒ (1 2 3)
(list 1 2 3)                      ;; ⇒ (1 2 3)
'(1 2 3)                           ;; ⇒ (1 2 3)
```

빈 리스트 `'()` 는 페어가 아니다 (`(pair? '())` ⇒ #f).
정상 리스트는 *페어의 사슬*에 *빈 리스트로 끝맺음*된 것.

### 21.3 점 페어와 부적절 리스트

```scheme
(cons 1 (cons 2 3))   ;; ⇒ (1 2 . 3)
```

이는 *부적절 리스트*. 끝이 빈 리스트가 아니다.
`(list? ...)`은 #f를 돌려준다.

### 21.4 흔한 절차 한 묶음

```scheme
(length '(a b c d))                ;; ⇒ 4
(reverse '(1 2 3))                 ;; ⇒ (3 2 1)
(append '(1 2) '(3 4) '(5))        ;; ⇒ (1 2 3 4 5)
(list-ref '(a b c d) 2)            ;; ⇒ c
(list-tail '(a b c d) 2)           ;; ⇒ (c d)
(member 3 '(1 2 3 4))              ;; ⇒ (3 4)
(memq 'b '(a b c))                 ;; ⇒ (b c)
(assq 'b '((a 1) (b 2) (c 3)))     ;; ⇒ (b 2)
(assoc "b" '(("a" 1) ("b" 2)))     ;; ⇒ ("b" 2)
```

`memq`/`assq`는 `eq?`, `memv`/`assv`는 `eqv?`, `member`/`assoc`는 `equal?`로 비교한다.

### 21.5 c…r 합성

`cadr`는 `(car (cdr ...))`. R7RS는 4단계까지 정의.

```scheme
(define p '((1 2) (3 4) (5 6)))
(car p)        ;; ⇒ (1 2)
(cadr p)       ;; ⇒ (3 4)
(caddr p)      ;; ⇒ (5 6)
(caar p)       ;; ⇒ 1
(cadar p)      ;; ⇒ 2
```

읽는 법: 안에서 바깥으로 — `cadr` = c**a**d**r** = car of (cdr ...).

### 21.6 자주 쓰는 헬퍼 직접 만들기

```scheme
(define (last-pair xs)
  (if (null? (cdr xs)) xs
      (last-pair (cdr xs))))

(define (last xs) (car (last-pair xs)))

(define (drop-last xs)
  (cond ((null? xs) '())
        ((null? (cdr xs)) '())
        (else (cons (car xs) (drop-last (cdr xs))))))

(last '(a b c d))         ;; ⇒ d
(drop-last '(a b c d))    ;; ⇒ (a b c)

(define (take xs n)
  (if (or (zero? n) (null? xs)) '()
      (cons (car xs) (take (cdr xs) (- n 1)))))

(define (drop xs n)
  (if (or (zero? n) (null? xs)) xs
      (drop (cdr xs) (- n 1))))

(take '(1 2 3 4 5) 3)     ;; ⇒ (1 2 3)
(drop '(1 2 3 4 5) 3)     ;; ⇒ (4 5)
```

### 21.7 가변 페어 — `set-car!` / `set-cdr!`

R6RS+ 또는 처리계 옵션에 의존. 함수형 코드에선 피하라.

```scheme
(define p (cons 1 2))
(set-car! p 'A) (set-cdr! p 'B)
p             ;; ⇒ (A . B)
```

### 21.8 순환 리스트

`set-cdr!`로 만들 수 있다.

```scheme
(define x (list 1 2 3))
(set-cdr! (cddr x) x)
;; (1 2 3 1 2 3 1 2 3 ...)
```

처리계마다 출력 형식 다름. `length`/`reverse`는 무한 루프하니 주의.

### 21.9 연습문제

1. `(count xs)` — fold 없이 길이를 직접 계산.
2. `(remove-dupes xs)` — `equal?` 기준 중복 제거.
3. `(zip xs ys)` — 두 리스트를 페어 리스트로 합침.
4. `(rotate xs n)` — 리스트를 n칸 회전.
5. `(deep-reverse t)` — 중첩 리스트의 모든 수준에서 뒤집기.

\newpage

## 22장 연관 리스트와 속성표

### 22.1 alist

키-값 페어의 리스트. 가벼운 사전 대용.

```scheme
(define ages '((alice . 30) (bob . 25) (carol . 35)))

(assq 'bob ages)              ;; ⇒ (bob . 25)
(cdr (assq 'bob ages))        ;; ⇒ 25

;; 추가
(define ages2 (cons (cons 'dan 40) ages))

;; 갱신(불변 형태) — 키를 찾아 새 alist
(define (alist-update k v alist)
  (cond ((null? alist) (list (cons k v)))
        ((eq? (caar alist) k)
         (cons (cons k v) (cdr alist)))
        (else (cons (car alist) (alist-update k v (cdr alist))))))

(alist-update 'bob 99 ages)
;; ⇒ ((alice . 30) (bob . 99) (carol . 35))
```

### 22.2 alist 헬퍼 모음

```scheme
(define (alist-keys a)   (map car a))
(define (alist-values a) (map cdr a))

(define (alist-merge a b)        ; b가 우선
  (let loop ((a a) (acc b))
    (cond ((null? a) acc)
          ((assq (caar a) acc) (loop (cdr a) acc))
          (else (loop (cdr a) (cons (car a) acc))))))

(alist-merge '((a . 1) (b . 2)) '((b . 99) (c . 3)))
;; ⇒ ((a . 1) (b . 99) (c . 3))
```

### 22.3 속성표(property list, plist) — 평탄 alist

Lisp 전통의 평탄 표현.

```scheme
;; '(name "Alice" age 30 city "Seoul")

(define (plist-get plist k)
  (cond ((null? plist) #f)
        ((eq? (car plist) k) (cadr plist))
        (else (plist-get (cddr plist) k))))

(plist-get '(name "Alice" age 30 city "Seoul") 'age)
;; ⇒ 30
```

### 22.4 alist의 시간 복잡도

`assq`는 *선형 검색*. 큰 사전엔 부적절 — 24장의 해시 테이블을 써라.
다만 작은 사전(<32항목)에선 alist가 더 빠른 경우도 많다.

### 22.5 *불변 사전* 패턴

함수형 갱신은 새 alist를 만든다. 메모리 비용 = O(n)이지만 락이 없고
공유가 안전하다. 동시성 코드에서 유용.

### 22.6 연습문제

1. `(alist->plist a)` 와 그 역인 `(plist->alist p)` 를 작성.
2. *기본값* 인자를 받는 `(alist-ref a k def)`.
3. 두 alist의 *key 교집합*만 남기는 함수.
4. 동일 키가 여러 번 나오는 alist를 *키별로 값 리스트로 그룹화*.

\newpage

## 23장 벡터와 다차원 배열

### 23.1 벡터의 기본

벡터는 *상수 시간 임의 접근*이 가능한 1차원 배열.

```scheme
(vector 1 2 3 4)                  ;; ⇒ #(1 2 3 4)
(make-vector 5 0)                 ;; ⇒ #(0 0 0 0 0)
(vector-length #(a b c))          ;; ⇒ 3
(vector-ref #(a b c) 1)           ;; ⇒ b
(define v (make-vector 3 0))
(vector-set! v 1 99)
v                                 ;; ⇒ #(0 99 0)
```

리터럴 `#(a b c)`는 리터럴 리스트 `'(a b c)`처럼 *상수* — 변경 금지.

### 23.2 변환

```scheme
(vector->list #(1 2 3))           ;; ⇒ (1 2 3)
(list->vector '(a b c))           ;; ⇒ #(a b c)
```

### 23.3 `vector-map` / `vector-for-each` / `vector-fill!`

```scheme
(vector-map (lambda (x) (* x x)) #(1 2 3 4))
;; ⇒ #(1 4 9 16)

(define v (make-vector 5 0))
(vector-fill! v 7)
v                                 ;; ⇒ #(7 7 7 7 7)

(vector-for-each
  (lambda (x) (display x) (display " "))
  #(a b c))
;; → a b c
```

### 23.4 다차원 배열 — 평면 인덱싱

```scheme
;; 3x4 행렬을 길이 12 벡터로 표현 (row-major)
(define (make-matrix rows cols init)
  (vector rows cols (make-vector (* rows cols) init)))

(define (mat-rows m) (vector-ref m 0))
(define (mat-cols m) (vector-ref m 1))
(define (mat-data m) (vector-ref m 2))

(define (mat-ref m r c)
  (vector-ref (mat-data m) (+ (* r (mat-cols m)) c)))

(define (mat-set! m r c v)
  (vector-set! (mat-data m) (+ (* r (mat-cols m)) c) v))

(define M (make-matrix 3 4 0))
(mat-set! M 1 2 99)
(mat-ref M 1 2)                   ;; ⇒ 99
```

### 23.5 행렬 곱

```scheme
(define (mat-mul A B)
  (let* ((rA (mat-rows A)) (cA (mat-cols A))
         (rB (mat-rows B)) (cB (mat-cols B)))
    (unless (= cA rB) (error "mismatch"))
    (let ((C (make-matrix rA cB 0)))
      (do ((i 0 (+ i 1))) ((= i rA))
        (do ((j 0 (+ j 1))) ((= j cB))
          (let loop ((k 0) (s 0))
            (if (= k cA)
                (mat-set! C i j s)
                (loop (+ k 1)
                      (+ s (* (mat-ref A i k) (mat-ref B k j))))))))
      C)))
```

### 23.6 벡터의 비용

| 연산 | 시간 |
| :--- | :--- |
| `vector-ref` / `vector-set!` | O(1) |
| `vector-length` | O(1) |
| `vector-fill!` | O(n) |
| `vector-copy` | O(n) |
| 끝에 추가 | 직접 O(n) (새 벡터 만듦) |

가변 길이가 필요하면 *동적 배열* 자료구조를 직접 만들어야 한다.

### 23.7 동적 배열(가변 길이 벡터)

```scheme
(define (make-dynvec)
  (cons 0 (make-vector 4 #f)))   ; (count . backing)

(define (dv-len d) (car d))

(define (dv-cap d) (vector-length (cdr d)))

(define (dv-ref d i) (vector-ref (cdr d) i))

(define (dv-push! d x)
  (when (= (dv-len d) (dv-cap d))
    (let* ((old (cdr d))
           (new (make-vector (* 2 (dv-cap d)) #f)))
      (vector-copy! new 0 old)
      (set-cdr! d new)))
  (vector-set! (cdr d) (dv-len d) x)
  (set-car! d (+ (dv-len d) 1)))

(define (dv-pop! d)
  (when (zero? (dv-len d)) (error "empty"))
  (set-car! d (- (dv-len d) 1))
  (vector-ref (cdr d) (dv-len d)))

(define D (make-dynvec))
(dv-push! D 'a) (dv-push! D 'b) (dv-push! D 'c)
(dv-len D)        ;; ⇒ 3
(dv-pop! D)       ;; ⇒ c
(dv-len D)        ;; ⇒ 2
```

(`vector-copy!`는 R7RS 정의. 처리계가 없으면 직접 루프로 복사.)

### 23.8 연습문제

1. 1차원 벡터에서 *최댓값과 그 위치*를 한 번 순회로 찾는 절차.
2. 위 행렬을 사용해 *전치(transpose)*.
3. 동적 배열에 `dv-insert!`/`dv-delete!`를 추가.
4. *원형 큐*를 고정 크기 벡터로 구현. enqueue/dequeue가 모두 O(1).

\newpage

## 24장 해시 테이블

### 24.1 R7RS와 해시 테이블

R7RS-small에는 해시 테이블이 표준이 아니다 — 처리계 라이브러리에 의존.
이식 가능한 미니 해시 테이블을 직접 만들어 보자(체이닝).

### 24.2 단순 해시 테이블

```scheme
(define (make-hash-table . args)
  ;; 생성: (count . buckets)
  (let ((cap (if (null? args) 16 (car args))))
    (vector 0 (make-vector cap '()))))

(define (ht-count h) (vector-ref h 0))
(define (ht-cap h)   (vector-length (vector-ref h 1)))
(define (ht-buckets h) (vector-ref h 1))

(define (str-hash s)
  ;; 간단한 djb2
  (let loop ((i 0) (h 5381))
    (if (= i (string-length s)) h
        (loop (+ i 1)
              (modulo (+ (* h 33) (char->integer (string-ref s i)))
                      #x7fffffff)))))

(define (ht-hash k)
  (cond ((number? k) (modulo (abs (exact (round k))) #x7fffffff))
        ((symbol? k) (str-hash (symbol->string k)))
        ((string? k) (str-hash k))
        (else 0)))

(define (ht-set! h k v)
  (let* ((idx (modulo (ht-hash k) (ht-cap h)))
         (bucket (vector-ref (ht-buckets h) idx))
         (cell (assoc k bucket)))
    (if cell
        (set-cdr! cell v)
        (begin
          (vector-set! (ht-buckets h) idx (cons (cons k v) bucket))
          (vector-set! h 0 (+ (ht-count h) 1)))))
  (when (> (ht-count h) (* 2 (ht-cap h))) (ht-rehash! h)))

(define (ht-ref h k . default)
  (let* ((idx (modulo (ht-hash k) (ht-cap h)))
         (bucket (vector-ref (ht-buckets h) idx))
         (cell (assoc k bucket)))
    (cond (cell (cdr cell))
          ((null? default) #f)
          (else (car default)))))

(define (ht-delete! h k)
  (let* ((idx (modulo (ht-hash k) (ht-cap h)))
         (bucket (vector-ref (ht-buckets h) idx)))
    (let loop ((bs bucket) (acc '()))
      (cond ((null? bs) #f)
            ((equal? (caar bs) k)
             (vector-set! (ht-buckets h) idx (append (reverse acc) (cdr bs)))
             (vector-set! h 0 (- (ht-count h) 1))
             #t)
            (else (loop (cdr bs) (cons (car bs) acc)))))))

(define (ht-rehash! h)
  (let* ((old-buckets (ht-buckets h))
         (new-cap (* 2 (vector-length old-buckets)))
         (new-buckets (make-vector new-cap '())))
    (vector-set! h 1 new-buckets)
    (vector-set! h 0 0)
    (let outer ((i 0))
      (when (< i (vector-length old-buckets))
        (for-each (lambda (cell) (ht-set! h (car cell) (cdr cell)))
                  (vector-ref old-buckets i))
        (outer (+ i 1))))))
```

### 24.3 사용

```scheme
(define h (make-hash-table))
(ht-set! h 'a 1)
(ht-set! h 'b 2)
(ht-set! h "name" "Alice")

(ht-ref h 'a)              ;; ⇒ 1
(ht-ref h "name")          ;; ⇒ "Alice"
(ht-ref h 'missing 'none)  ;; ⇒ none

(ht-delete! h 'a)          ;; ⇒ #t
(ht-ref h 'a)              ;; ⇒ #f
```

### 24.4 처리계별 해시 테이블

| 처리계 | 생성 | 조회 | 갱신 |
| :--- | :--- | :--- | :--- |
| Racket | `(make-hash)` | `(hash-ref h k def)` | `(hash-set! h k v)` |
| Chez | `(make-hashtable hash equal?)` | `(hashtable-ref h k def)` | `(hashtable-set! h k v)` |
| Chibi | `(make-hash-table equal?)` | `(hash-table-ref h k def)` | `(hash-table-set! h k v)` |

이식 코드는 24.2의 미니 구현이나 SRFI-69를 쓴다.

### 24.5 단어 빈도(다시)

```scheme
(define (word-freq text)
  (define h (make-hash-table))
  (for-each
    (lambda (w)
      (ht-set! h w (+ 1 (or (ht-ref h w) 0))))
    (string-split text #\space))
  ;; 결과 alist
  (let loop ((i 0) (acc '()))
    (if (= i (ht-cap h)) acc
        (loop (+ i 1)
              (append (vector-ref (ht-buckets h) i) acc)))))

(word-freq "the quick brown fox the lazy dog the fox")
;; ⇒ ((the . 3) (fox . 2) ...) (순서 보장 X)
```

(`string-split`은 6장 참고.)

### 24.6 해시 테이블 vs alist

| 척도 | alist | 해시 테이블 |
| :--- | :--- | :--- |
| 구현 복잡도 | 매우 단순 | 보통 |
| 작은 크기 | 매우 빠름 | 적당 |
| 큰 크기 | O(n) 검색 | O(1) 평균 |
| 불변성 | 자연스러움 | 가변 기본 |
| 직렬화 | `write`로 그대로 | 변환 필요 |

### 24.7 연습문제

1. 위 해시 테이블에 `(ht-keys h)` 와 `(ht-values h)` 를 추가.
2. *open addressing* 방식으로 다시 구현.
3. 충돌이 많을 때 *체이닝 → 트리*(자주 보이는 키만 트리화)하는 변형.
4. *순서를 유지*하는 LinkedHashMap 변형.

\newpage

## 25장 문자열 기반 자료 구조

### 25.1 텍스트 처리 패턴

#### 토크나이저

```scheme
(define (tokenize s)
  (let loop ((i 0) (start #f) (acc '()))
    (define (push end)
      (if start (cons (substring s start end) acc) acc))
    (cond ((>= i (string-length s))
           (reverse (push i)))
          ((char-whitespace? (string-ref s i))
           (loop (+ i 1) #f (push i)))
          (else
           (loop (+ i 1) (or start i) acc)))))

(tokenize "  the  quick  brown   fox  ")
;; ⇒ ("the" "quick" "brown" "fox")
```

#### 패턴 매칭(글로브)

```scheme
;; * 와 ? 만 지원
(define (glob-match pat s)
  (let m ((pi 0) (si 0))
    (cond ((= pi (string-length pat)) (= si (string-length s)))
          ((char=? (string-ref pat pi) #\*)
           (or (m (+ pi 1) si)
               (and (< si (string-length s))
                    (m pi (+ si 1)))))
          ((>= si (string-length s)) #f)
          ((or (char=? (string-ref pat pi) #\?)
               (char=? (string-ref pat pi) (string-ref s si)))
           (m (+ pi 1) (+ si 1)))
          (else #f))))

(glob-match "*.scm" "hello.scm")    ;; ⇒ #t
(glob-match "h?llo" "hello")        ;; ⇒ #t
(glob-match "h?llo" "world")        ;; ⇒ #f
```

### 25.2 문자열 빌더 패턴

문자열 결합은 매번 새 문자열을 만들기 때문에 누적 시 O(n²).
`open-output-string`을 쓰면 O(n).

```scheme
(define (build-csv rows)
  (let ((p (open-output-string)))
    (for-each
      (lambda (row)
        (for-each
          (lambda (i)
            (when (> i 0) (display "," p))
            (display (list-ref row i) p))
          (iota (length row)))
        (newline p))
      rows)
    (get-output-string p)))

(define (iota n) (let loop ((i 0) (a '()))
                   (if (= i n) (reverse a) (loop (+ i 1) (cons i a)))))

(build-csv '((1 2 3) (4 5 6)))
;; ⇒ "1,2,3\n4,5,6\n"
```

### 25.3 문자 집합

R7RS-small엔 문자 집합 표준이 빈약. 직접 만들거나 SRFI-14.

```scheme
(define (char-in? c s)
  (let loop ((i 0))
    (cond ((>= i (string-length s)) #f)
          ((char=? c (string-ref s i)) #t)
          (else (loop (+ i 1))))))

(define digits "0123456789")
(char-in? #\3 digits)   ;; ⇒ #t
```

### 25.4 가벼운 정규표현 — 토큰화 그리기

본격 정규표현은 SRFI-115 / 처리계 라이브러리에 의존. 가벼운 유한오토마톤은
이후 39장(KMP)에서 다룬다.

### 25.5 연습문제

1. *trim* — 좌/우 공백 제거.
2. *replace-all* — 부분 문자열을 다른 문자열로 모두 치환.
3. *justify* — 너비에 맞게 좌·우·가운데 정렬.
4. CSV 한 줄 파싱 — 따옴표로 둘러싼 콤마 처리.

\newpage

## 26장 레코드(`define-record-type`)

### 26.1 R7RS의 레코드

```scheme
(define-record-type 점
  (make-point x y)         ; 생성자
  point?                   ; 술어
  (x point-x set-point-x!) ; 필드: 접근자, (선택) 변경자
  (y point-y))

(define p (make-point 3 4))
(point? p)        ;; ⇒ #t
(point-x p)       ;; ⇒ 3
(point-y p)       ;; ⇒ 4
(set-point-x! p 10)
(point-x p)       ;; ⇒ 10
```

`set-...!` 변경자가 없으면 그 필드는 *불변*.

### 26.2 레코드의 의미

다른 언어의 *구조체/클래스*에 가깝다. `equal?`는 보통 *모든 필드 동일*을 확인하지만
처리계마다 다르므로 비교 절차를 명시적으로 작성하라.

```scheme
(define (point=? p q)
  (and (point? p) (point? q)
       (equal? (point-x p) (point-x q))
       (equal? (point-y p) (point-y q))))
```

### 26.3 예제 — 가계도

```scheme
(define-record-type person
  (make-person name age children)
  person?
  (name person-name)
  (age  person-age)
  (children person-children set-person-children!))

(define alice (make-person 'alice 60 '()))
(define bob   (make-person 'bob 35 '()))
(define carol (make-person 'carol 33 '()))
(set-person-children! alice (list bob carol))

(map person-name (person-children alice))
;; ⇒ (bob carol)
```

### 26.4 함수형 레코드 — *with-update*

R7RS는 자동 with-update를 주지 않는다. 헬퍼:

```scheme
(define (point-with-x p new-x)
  (make-point new-x (point-y p)))

(define p2 (point-with-x p 7))
(point-x p2)                  ;; ⇒ 7
(point-x p)                   ;; ⇒ 10  (불변 사용 시)
```

### 26.5 직렬화

레코드를 alist로 바꿔 저장하는 패턴.

```scheme
(define (point->alist p)
  (list (cons 'x (point-x p)) (cons 'y (point-y p))))

(define (alist->point a)
  (make-point (cdr (assq 'x a)) (cdr (assq 'y a))))
```

### 26.6 연습문제

1. `define-record-type`로 *원*을 정의(중심점, 반지름). 면적/둘레 절차.
2. *원/사각형/삼각형*을 통합한 *도형* 인터페이스. 다형 절차 `area`.
3. *불변* 레코드와 `with-...` 헬퍼를 자동 생성하는 매크로.
4. 레코드 직렬화·역직렬화의 일반화.

\newpage

## 27장 트리

### 27.1 이진 트리 표현

```scheme
;; (val left right) 형식, 빈 트리는 #f
(define (make-tree v l r) (list v l r))
(define (tree-val t)   (car t))
(define (tree-left t)  (cadr t))
(define (tree-right t) (caddr t))
(define (empty-tree? t) (eq? t #f))
```

또는 레코드:

```scheme
(define-record-type bnode
  (make-bnode val left right) bnode?
  (val bnode-val)
  (left bnode-left)
  (right bnode-right))
```

### 27.2 순회

```scheme
(define (tree-inorder t)
  (if (empty-tree? t) '()
      (append (tree-inorder (tree-left t))
              (cons (tree-val t)
                    (tree-inorder (tree-right t))))))

(define (tree-preorder t)
  (if (empty-tree? t) '()
      (cons (tree-val t)
            (append (tree-preorder (tree-left t))
                    (tree-preorder (tree-right t))))))

(define (tree-postorder t)
  (if (empty-tree? t) '()
      (append (tree-postorder (tree-left t))
              (tree-postorder (tree-right t))
              (list (tree-val t)))))
```

```scheme
(define t
  (make-tree 1
    (make-tree 2 #f #f)
    (make-tree 3 (make-tree 4 #f #f) #f)))

(tree-inorder t)    ;; ⇒ (2 1 4 3)
(tree-preorder t)   ;; ⇒ (1 2 3 4)
(tree-postorder t)  ;; ⇒ (2 4 3 1)
```

### 27.3 BST(이진 탐색 트리)

```scheme
(define (bst-insert t k)
  (cond ((empty-tree? t) (make-tree k #f #f))
        ((< k (tree-val t))
         (make-tree (tree-val t)
                    (bst-insert (tree-left t) k)
                    (tree-right t)))
        ((> k (tree-val t))
         (make-tree (tree-val t)
                    (tree-left t)
                    (bst-insert (tree-right t) k)))
        (else t)))

(define (bst-contains? t k)
  (cond ((empty-tree? t) #f)
        ((= k (tree-val t)) #t)
        ((< k (tree-val t)) (bst-contains? (tree-left t) k))
        (else (bst-contains? (tree-right t) k))))

(define b (fold-left bst-insert #f '(5 3 8 1 4 7 9)))
(bst-contains? b 4)       ;; ⇒ #t
(bst-contains? b 6)       ;; ⇒ #f
(tree-inorder b)          ;; ⇒ (1 3 4 5 7 8 9)
```

### 27.4 BST의 한계와 균형 트리

균형이 깨지면 (`fold-left bst-insert #f '(1 2 3 4 5))`) 트리가 한 줄이 되어 O(n).
*AVL*, *적흑(red-black)*, *splay*로 균형을 유지한다.

### 27.5 AVL 트리

각 노드의 *높이 차 ≤ 1*.

```scheme
(define-record-type avl
  (make-avl val height left right) avl?
  (val avl-val)
  (height avl-h)
  (left avl-l)
  (right avl-r))

(define (h t) (if (eq? t #f) 0 (avl-h t)))

(define (mk v l r) (make-avl v (+ 1 (max (h l) (h r))) l r))

(define (rot-r t)
  (let ((l (avl-l t)))
    (mk (avl-val l) (avl-l l) (mk (avl-val t) (avl-r l) (avl-r t)))))

(define (rot-l t)
  (let ((r (avl-r t)))
    (mk (avl-val r) (mk (avl-val t) (avl-l t) (avl-l r)) (avl-r r))))

(define (balance t)
  (let ((bf (- (h (avl-l t)) (h (avl-r t)))))
    (cond ((> bf 1)
           (if (< (- (h (avl-l (avl-l t))) (h (avl-r (avl-l t)))) 0)
               (rot-r (mk (avl-val t) (rot-l (avl-l t)) (avl-r t)))
               (rot-r t)))
          ((< bf -1)
           (if (> (- (h (avl-l (avl-r t))) (h (avl-r (avl-r t)))) 0)
               (rot-l (mk (avl-val t) (avl-l t) (rot-r (avl-r t))))
               (rot-l t)))
          (else t))))

(define (avl-insert t k)
  (cond ((eq? t #f) (mk k #f #f))
        ((< k (avl-val t))
         (balance (mk (avl-val t) (avl-insert (avl-l t) k) (avl-r t))))
        ((> k (avl-val t))
         (balance (mk (avl-val t) (avl-l t) (avl-insert (avl-r t) k))))
        (else t)))

(define A (fold-left avl-insert #f '(1 2 3 4 5 6 7)))
(h A)   ;; ⇒ 3   (편향 BST라면 7이 됐을 것)
```

### 27.6 적흑 트리(개요)

각 노드는 빨강/검정. 다섯 가지 불변식이 균형을 보장 — Okasaki의 함수형 적흑 삽입은
교과서적이다(이 책 부록 D 참고).

### 27.7 일반(rose) 트리

자식이 임의 개수.

```scheme
;; (val children-list)
(define (rose v cs) (cons v cs))
(define (rose-val n) (car n))
(define (rose-children n) (cdr n))

(define (rose-size n)
  (+ 1 (apply + (map rose-size (rose-children n)))))

(rose-size (rose 'a (list (rose 'b '()) (rose 'c (list (rose 'd '()))))))
;; ⇒ 4
```

### 27.8 트리 시각화 (텍스트)

```scheme
(define (print-tree t indent)
  (when (not (empty-tree? t))
    (print-tree (tree-right t) (+ indent 4))
    (display (make-string indent #\space))
    (display (tree-val t)) (newline)
    (print-tree (tree-left t) (+ indent 4))))

(print-tree b 0)
```

### 27.9 연습문제

1. BST의 `delete` 구현 (오른쪽 서브트리의 최솟값으로 대체).
2. 트리 *깊이*와 *노드 수*.
3. *대칭 트리* 판정 — 좌우가 거울인가?
4. AVL의 `delete` 구현.
5. *어떤 키든 가까운 두 값 사이에 있는가*(in-order successor/predecessor)를 구하는 절차.

\newpage

## 28장 힙(우선순위 큐)

### 28.1 이진 힙(배열 표현)

부모 인덱스 `i` → 자식 `2i+1`, `2i+2`. 0번 인덱스부터 사용.

```scheme
;; min-heap, 동적배열 위에 구축

(define (make-heap)
  (cons 0 (make-vector 16 #f)))

(define (heap-len h) (car h))
(define (heap-cap h) (vector-length (cdr h)))
(define (heap-arr h) (cdr h))
(define (heap-ref h i) (vector-ref (heap-arr h) i))
(define (heap-set! h i v) (vector-set! (heap-arr h) i v))

(define (heap-grow! h)
  (let ((new (make-vector (* 2 (heap-cap h)) #f)))
    (do ((i 0 (+ i 1))) ((= i (heap-len h)))
      (vector-set! new i (heap-ref h i)))
    (set-cdr! h new)))

(define (heap-swap! h i j)
  (let ((t (heap-ref h i)))
    (heap-set! h i (heap-ref h j))
    (heap-set! h j t)))

(define (heap-up! h i)
  (when (> i 0)
    (let ((p (quotient (- i 1) 2)))
      (when (< (heap-ref h i) (heap-ref h p))
        (heap-swap! h i p)
        (heap-up! h p)))))

(define (heap-down! h i)
  (let* ((n (heap-len h))
         (l (+ (* 2 i) 1)) (r (+ (* 2 i) 2)))
    (let ((s (if (and (< l n) (< (heap-ref h l) (heap-ref h i))) l i)))
      (let ((s (if (and (< r n) (< (heap-ref h r) (heap-ref h s))) r s)))
        (when (not (= s i))
          (heap-swap! h i s)
          (heap-down! h s))))))

(define (heap-push! h x)
  (when (= (heap-len h) (heap-cap h)) (heap-grow! h))
  (heap-set! h (heap-len h) x)
  (set-car! h (+ (heap-len h) 1))
  (heap-up! h (- (heap-len h) 1)))

(define (heap-pop! h)
  (when (zero? (heap-len h)) (error "empty"))
  (let ((top (heap-ref h 0)))
    (set-car! h (- (heap-len h) 1))
    (heap-set! h 0 (heap-ref h (heap-len h)))
    (heap-down! h 0)
    top))
```

### 28.2 사용

```scheme
(define h (make-heap))
(heap-push! h 5)
(heap-push! h 1)
(heap-push! h 3)
(heap-push! h 2)
(heap-pop! h)    ;; ⇒ 1
(heap-pop! h)    ;; ⇒ 2
(heap-pop! h)    ;; ⇒ 3
(heap-pop! h)    ;; ⇒ 5
```

### 28.3 힙 정렬

```scheme
(define (heap-sort xs)
  (define h (make-heap))
  (for-each (lambda (x) (heap-push! h x)) xs)
  (let loop ((acc '()))
    (if (zero? (heap-len h))
        (reverse acc)
        (loop (cons (heap-pop! h) acc)))))

(heap-sort '(5 3 8 1 9 2 7 4 6))   ;; ⇒ (1 2 3 4 5 6 7 8 9)
```

### 28.4 우선순위 큐 — 키와 값 분리

```scheme
;; (priority . payload) 페어를 키로 비교

(define (heap-up*! h i cmp)
  (when (> i 0)
    (let ((p (quotient (- i 1) 2)))
      (when (cmp (heap-ref h i) (heap-ref h p))
        (heap-swap! h i p)
        (heap-up*! h p cmp)))))
;; (생략 — heap-down도 cmp 인자화)
```

### 28.5 힙의 적용

- *우선순위 큐*: 작업 스케줄링.
- *Dijkstra*: 38장.
- *허프만 코딩*: 39장 보충 문제.
- *상위 K개*: 작은 힙으로 스트리밍 처리.

### 28.6 연습문제

1. *max-heap* 변형.
2. *키 변경*(decrease-key) — 인덱스 맵을 유지해 O(log n).
3. *힙으로 중앙값 유지* — 두 힙(상/하반).
4. 외부 메모리 정렬에 사용되는 *k-way merge*를 힙으로.

\newpage

## 29장 그래프 표현

### 29.1 인접 리스트

가장 보편적 표현.

```scheme
;; ((node . (neighbor1 neighbor2 ...)) ...)
(define G '((a . (b c))
            (b . (a d))
            (c . (a d))
            (d . (b c e))
            (e . (d))))

(define (neighbors g v)
  (cond ((assq v g) => cdr)
        (else '())))

(neighbors G 'd)   ;; ⇒ (b c e)
```

### 29.2 인접 행렬

작은 밀도 높은 그래프에 좋다. 0/1 또는 가중치.

```scheme
;; 행렬은 23장의 mat-* 사용
(define (matrix-graph n)
  (make-matrix n n 0))

(define (m-edge! g u v w)
  (mat-set! g u v w)
  (mat-set! g v u w))

(define G2 (matrix-graph 5))
(m-edge! G2 0 1 1)
(m-edge! G2 0 2 1)
(mat-ref G2 0 1)     ;; ⇒ 1
```

### 29.3 가중 그래프(인접 리스트)

```scheme
;; ((u . ((v . w) (v' . w') ...)) ...)
(define WG '((a . ((b . 4) (c . 1)))
             (b . ((a . 4) (c . 2) (d . 5)))
             (c . ((a . 1) (b . 2) (d . 8)))
             (d . ((b . 5) (c . 8)))))

(define (w-neighbors g v) (or (cdr (or (assq v g) (cons #f '()))) '()))

(w-neighbors WG 'b)    ;; ⇒ ((a . 4) (c . 2) (d . 5))
```

### 29.4 BFS / DFS는 38장에서 본격 다룸

여기서는 표현만 정리. 다음 장으로.

### 29.5 연습문제

1. 인접 리스트 ↔ 인접 행렬 변환.
2. 그래프에 *자가 루프* 또는 *중복 엣지* 검출.
3. 무방향에서 *이웃 일치*(symmetry) 검증.
4. *희소성* 통계 — 노드 수 N, 엣지 수 E, 평균 차수.

\newpage

## 30장 큐, 덱, 스택, 링버퍼

### 30.1 스택 = 리스트

```scheme
(define s '())
(set! s (cons 'a s))   ; push
(set! s (cons 'b s))
(car s)                ; top ⇒ b
(set! s (cdr s))       ; pop
```

12장의 클로저 캡슐화 버전을 권장.

### 30.2 큐 — 두 스택 트릭

```scheme
;; (front-stack . back-stack)
(define (make-queue) (cons '() '()))
(define (q-empty? q) (and (null? (car q)) (null? (cdr q))))

(define (q-push! q x) (set-cdr! q (cons x (cdr q))))

(define (q-pop! q)
  (when (null? (car q))
    (set-car! q (reverse (cdr q)))
    (set-cdr! q '()))
  (let ((x (car (car q))))
    (set-car! q (cdr (car q)))
    x))

(define Q (make-queue))
(q-push! Q 1) (q-push! Q 2) (q-push! Q 3)
(q-pop! Q)     ;; ⇒ 1
(q-pop! Q)     ;; ⇒ 2
(q-pop! Q)     ;; ⇒ 3
```

분할상환 시간 O(1).

### 30.3 덱(double-ended queue)

양쪽 push/pop. 두 스택만으로는 한쪽 비면 이상치가 생기므로
*양쪽 스택의 균형 유지* 또는 *원형 버퍼*가 일반적.

### 30.4 링 버퍼(원형 큐)

고정 크기 벡터.

```scheme
(define (make-ring n)
  (vector 0 0 0 (make-vector n #f)))    ; (head tail size data)

(define (r-data r) (vector-ref r 3))
(define (r-cap r)  (vector-length (r-data r)))
(define (r-size r) (vector-ref r 2))

(define (r-push! r x)
  (when (= (r-size r) (r-cap r)) (error "full"))
  (let ((t (vector-ref r 1)))
    (vector-set! (r-data r) t x)
    (vector-set! r 1 (modulo (+ t 1) (r-cap r)))
    (vector-set! r 2 (+ (r-size r) 1))))

(define (r-pop! r)
  (when (zero? (r-size r)) (error "empty"))
  (let* ((h (vector-ref r 0))
         (x (vector-ref (r-data r) h)))
    (vector-set! r 0 (modulo (+ h 1) (r-cap r)))
    (vector-set! r 2 (- (r-size r) 1))
    x))

(define R (make-ring 4))
(r-push! R 1) (r-push! R 2) (r-push! R 3)
(r-pop! R)     ;; ⇒ 1
(r-push! R 4) (r-push! R 5)
(r-pop! R)     ;; ⇒ 2
```

### 30.5 양방향 연결 리스트(가변)

```scheme
;; 노드: (prev val next), 각 필드는 set-car!/cdr! 가능 페어
(define (mk-dnode v) (vector #f v #f))
(define (dn-prev n) (vector-ref n 0))
(define (dn-val n)  (vector-ref n 1))
(define (dn-next n) (vector-ref n 2))
(define (dn-set-prev! n p) (vector-set! n 0 p))
(define (dn-set-next! n p) (vector-set! n 2 p))

(define (dl-insert-after! n v)
  (let ((m (mk-dnode v))
        (nxt (dn-next n)))
    (dn-set-next! m nxt)
    (dn-set-prev! m n)
    (when nxt (dn-set-prev! nxt m))
    (dn-set-next! n m)
    m))

(define (dl-walk n)
  (if n
      (cons (dn-val n) (dl-walk (dn-next n)))
      '()))

(define head (mk-dnode 'a))
(dl-insert-after! head 'b)
(dl-insert-after! head 'c)
(dl-walk head)      ;; ⇒ (a c b)
```

### 30.6 연습문제

1. *Bracket-balance* 검사 — 스택으로.
2. 위 큐를 *스레드 안전*하게(처리계 의존, mutex 흉내).
3. 링 버퍼 위에 덱 구현(양방향 push/pop).
4. *고정 크기 LRU 캐시*를 양방향 리스트 + 해시 테이블로 구현.

\newpage
# 4부 알고리즘

\newpage

## 31장 알고리즘 분석 기초

### 31.1 점근 표기

| 표기 | 의미 | 예 |
| :--- | :--- | :--- |
| O(f) | 상한 — *최악 경우* | 정렬: O(n²) |
| Ω(f) | 하한 — *최선 경우* | 비교 정렬: Ω(n log n) |
| Θ(f) | 정확 차수 | 합: Θ(n) |

### 31.2 대표적 함수의 성장

```
1 < log n < n < n log n < n² < n³ < 2^n < n!
```

n=1000 일 때:
- log n ≈ 10
- n log n ≈ 10000
- n² = 1,000,000
- n³ = 1,000,000,000
- 2ⁿ ≈ 10³⁰¹

### 31.3 Scheme 절차의 비용

| 연산 | 시간 |
| :--- | :--- |
| `cons` / `car` / `cdr` | O(1) |
| `length` | O(n) |
| `list-ref` / `list-tail` | O(n) |
| `append` | O(n) — 첫 인자 길이 |
| `reverse` | O(n) |
| `vector-ref` / `vector-set!` | O(1) |
| `equal?` | O(n) — 구조 크기 |

알고리즘 분석 시 *기본 연산이 무엇인지*를 먼저 분명히 하라.

### 31.4 측정 코드

```scheme
(define (time-thunk thunk)
  (let ((t0 (current-jiffy)))
    (let ((r (thunk)))
      (cons (/ (- (current-jiffy) t0) (jiffies-per-second)) r))))

;; 사용
(time-thunk (lambda () (sum-1-to-n 1000000)))
;; ⇒ (0.012 . 500000500000)
```

(`current-jiffy`/`jiffies-per-second`는 R7RS `(scheme time)`.)

### 31.5 연습문제

1. 다음 식의 점근 시간:
   - `(map f (map g xs))`
   - `(reverse (map f xs))`
   - `(append (map f xs) (reverse xs))`
2. *순진한 fib*와 *누적자 fib*의 시간 차이를 직접 측정.
3. *해시 테이블 크기*에 따른 lookup 시간 측정.

\newpage

## 32장 정렬

### 32.1 버블 정렬 — 교육용

```scheme
;; 리스트는 비효율 — 벡터로

(define (bubble-sort! v)
  (let ((n (vector-length v)))
    (do ((i 0 (+ i 1))) ((= i n))
      (do ((j 0 (+ j 1))) ((= j (- n i 1)))
        (when (> (vector-ref v j) (vector-ref v (+ j 1)))
          (let ((t (vector-ref v j)))
            (vector-set! v j (vector-ref v (+ j 1)))
            (vector-set! v (+ j 1) t)))))
    v))

(bubble-sort! (vector 5 2 4 1 3))   ;; ⇒ #(1 2 3 4 5)
```

O(n²) — 작은 데이터 외에는 사용 금지.

### 32.2 삽입 정렬

```scheme
(define (insertion-sort! v)
  (let ((n (vector-length v)))
    (do ((i 1 (+ i 1))) ((= i n) v)
      (let ((x (vector-ref v i)))
        (let loop ((j (- i 1)))
          (cond ((and (>= j 0) (> (vector-ref v j) x))
                 (vector-set! v (+ j 1) (vector-ref v j))
                 (loop (- j 1)))
                (else (vector-set! v (+ j 1) x))))))))
```

O(n²) 최악, O(n) 부분 정렬된 데이터엔 매우 빠름.

### 32.3 선택 정렬

```scheme
(define (selection-sort! v)
  (let ((n (vector-length v)))
    (do ((i 0 (+ i 1))) ((= i (- n 1)) v)
      (let loop ((j (+ i 1)) (mn i))
        (cond ((= j n)
               (let ((t (vector-ref v i)))
                 (vector-set! v i (vector-ref v mn))
                 (vector-set! v mn t)))
              ((< (vector-ref v j) (vector-ref v mn))
               (loop (+ j 1) j))
              (else (loop (+ j 1) mn)))))))
```

### 32.4 머지 정렬

리스트에 자연스럽다 — 순수 함수형.

```scheme
(define (merge a b)
  (cond ((null? a) b)
        ((null? b) a)
        ((<= (car a) (car b))
         (cons (car a) (merge (cdr a) b)))
        (else
         (cons (car b) (merge a (cdr b))))))

(define (split xs)
  (let loop ((slow xs) (fast xs) (left '()))
    (if (or (null? fast) (null? (cdr fast)))
        (values (reverse left) slow)
        (loop (cdr slow) (cddr fast) (cons (car slow) left)))))

(define (merge-sort xs)
  (if (or (null? xs) (null? (cdr xs))) xs
      (let-values (((l r) (split xs)))
        (merge (merge-sort l) (merge-sort r)))))

(merge-sort '(5 2 8 1 9 3 7 4 6))
;; ⇒ (1 2 3 4 5 6 7 8 9)
```

O(n log n) 보장. 안정 정렬.

### 32.5 퀵 정렬

리스트 버전(피벗 = 첫 원소).

```scheme
(define (quick-sort xs)
  (if (or (null? xs) (null? (cdr xs))) xs
      (let* ((p (car xs))
             (rest (cdr xs))
             (smaller (filter (lambda (x) (< x p)) rest))
             (larger  (filter (lambda (x) (>= x p)) rest)))
        (append (quick-sort smaller)
                (cons p (quick-sort larger))))))

(quick-sort '(5 2 8 1 9 3 7 4 6))
;; ⇒ (1 2 3 4 5 6 7 8 9)
```

평균 O(n log n), 최악 O(n²). 무작위 피벗 권장.

### 32.6 In-place 퀵 정렬(벡터)

```scheme
(define (qsort! v lo hi)
  (when (< lo hi)
    (let* ((pivot (vector-ref v hi))
           (i (let loop ((j lo) (i (- lo 1)))
                (cond ((= j hi) i)
                      ((<= (vector-ref v j) pivot)
                       (let ((t (vector-ref v (+ i 1))))
                         (vector-set! v (+ i 1) (vector-ref v j))
                         (vector-set! v j t))
                       (loop (+ j 1) (+ i 1)))
                      (else (loop (+ j 1) i))))))
      (let ((t (vector-ref v (+ i 1))))
        (vector-set! v (+ i 1) (vector-ref v hi))
        (vector-set! v hi t))
      (qsort! v lo i)
      (qsort! v (+ i 2) hi))))

(define (qsort v) (qsort! v 0 (- (vector-length v) 1)) v)

(qsort (vector 5 2 8 1 9 3 7 4 6))
;; ⇒ #(1 2 3 4 5 6 7 8 9)
```

### 32.7 힙 정렬

28장의 힙으로 자연스레.

### 32.8 카운팅 정렬

값 범위가 작을 때.

```scheme
(define (counting-sort xs k)
  (let ((cnt (make-vector (+ k 1) 0)))
    (for-each (lambda (x) (vector-set! cnt x (+ (vector-ref cnt x) 1))) xs)
    (let loop ((i 0) (acc '()))
      (cond ((> i k) (reverse acc))
            ((zero? (vector-ref cnt i)) (loop (+ i 1) acc))
            (else
             (vector-set! cnt i (- (vector-ref cnt i) 1))
             (loop i (cons i acc)))))))

(counting-sort '(3 1 4 1 5 9 2 6 5 3) 9)
;; ⇒ (1 1 2 3 3 4 5 5 6 9)
```

O(n + k). 비교 정렬 하한 Ω(n log n)을 *피해* 가는 비교 안 하는 정렬.

### 32.9 비교 함수 일반화

```scheme
(define (sort cmp xs)
  (if (or (null? xs) (null? (cdr xs))) xs
      (let* ((p (car xs))
             (rest (cdr xs))
             (lo (filter (lambda (x) (cmp x p)) rest))
             (hi (filter (lambda (x) (not (cmp x p))) rest)))
        (append (sort cmp lo) (cons p (sort cmp hi))))))

(sort < '(3 1 4 1 5 9 2 6))
;; ⇒ (1 1 2 3 4 5 6 9)

(sort string<?
      '("banana" "apple" "cherry"))
;; ⇒ ("apple" "banana" "cherry")
```

### 32.10 연습문제

1. *3-way 퀵 정렬* — 피벗과 같은 값을 따로 모음(중복 많을 때 빠름).
2. *Tim sort*의 핵심 아이디어를 정리.
3. *외부 정렬* — 메모리에 안 들어가는 데이터.
4. *기수 정렬*(LSD) 구현.

\newpage

## 33장 탐색

### 33.1 선형 검색

```scheme
(define (linear-search v x)
  (let loop ((i 0))
    (cond ((>= i (vector-length v)) #f)
          ((equal? (vector-ref v i) x) i)
          (else (loop (+ i 1))))))

(linear-search #(3 1 4 1 5 9 2 6) 5)   ;; ⇒ 4
(linear-search #(3 1 4 1 5 9 2 6) 7)   ;; ⇒ #f
```

### 33.2 이분 검색(정렬된 벡터)

```scheme
(define (binary-search v x)
  (let loop ((lo 0) (hi (- (vector-length v) 1)))
    (cond ((> lo hi) #f)
          (else
           (let* ((m (quotient (+ lo hi) 2))
                  (mv (vector-ref v m)))
             (cond ((= mv x) m)
                   ((< mv x) (loop (+ m 1) hi))
                   (else     (loop lo (- m 1)))))))))

(binary-search #(1 2 3 5 8 13 21 34) 13)   ;; ⇒ 5
(binary-search #(1 2 3 5 8 13 21 34) 7)    ;; ⇒ #f
```

O(log n).

### 33.3 *lower_bound* — 정렬에서 키 이상의 첫 위치

```scheme
(define (lower-bound v x)
  (let loop ((lo 0) (hi (vector-length v)))
    (if (>= lo hi) lo
        (let* ((m (quotient (+ lo hi) 2))
               (mv (vector-ref v m)))
          (if (< mv x)
              (loop (+ m 1) hi)
              (loop lo m))))))

(lower-bound #(1 3 5 7 9) 4)   ;; ⇒ 2  (값 5의 위치)
(lower-bound #(1 3 5 7 9) 5)   ;; ⇒ 2
(lower-bound #(1 3 5 7 9) 10)  ;; ⇒ 5
```

### 33.4 보간(interpolation) 검색

균등 분포 데이터에서 평균 O(log log n).

```scheme
(define (interp-search v x)
  (let loop ((lo 0) (hi (- (vector-length v) 1)))
    (cond ((or (> lo hi)
               (< x (vector-ref v lo))
               (> x (vector-ref v hi)))
           #f)
          (else
           (let* ((rg (- (vector-ref v hi) (vector-ref v lo)))
                  (pos (if (zero? rg) lo
                           (+ lo (quotient (* (- hi lo) (- x (vector-ref v lo))) rg)))))
             (cond ((= (vector-ref v pos) x) pos)
                   ((< (vector-ref v pos) x) (loop (+ pos 1) hi))
                   (else (loop lo (- pos 1)))))))))
```

### 33.5 연습문제

1. *upper_bound*도 작성.
2. 회전된 정렬 배열(`(4 5 6 1 2 3)`)에서 이분 검색.
3. *제곱근*을 이분 검색으로(정수만).
4. *피크 원소* 찾기(인접보다 큰 원소) — O(log n).

\newpage

## 34장 분할 정복

### 34.1 패러다임

1. **분할** — 부분문제로 쪼갠다.
2. **정복** — 부분문제를 재귀로 해결.
3. **결합** — 부분 해를 합친다.

머지 정렬, 퀵 정렬, 이분 검색이 모두 이 형식.

### 34.2 거듭제곱

```scheme
(define (pow b n)
  (cond ((zero? n) 1)
        ((even? n) (let ((h (pow b (quotient n 2)))) (* h h)))
        (else (* b (pow b (- n 1))))))

(pow 2 30)   ;; ⇒ 1073741824
```

O(log n).

### 34.3 카라추바 곱셈

큰 정수 곱셈의 분할 정복 — n자리 × n자리를 O(n^log₂3) ≈ O(n^1.585).

```scheme
(define (karatsuba x y)
  (cond ((or (< x 1000) (< y 1000)) (* x y))
        (else
         (let* ((n (max (string-length (number->string x))
                        (string-length (number->string y))))
                (m (quotient n 2))
                (10^m (expt 10 m))
                (xh (quotient x 10^m)) (xl (modulo x 10^m))
                (yh (quotient y 10^m)) (yl (modulo y 10^m))
                (z2 (karatsuba xh yh))
                (z0 (karatsuba xl yl))
                (z1 (- (karatsuba (+ xh xl) (+ yh yl)) z2 z0)))
           (+ (* z2 (expt 10 (* 2 m))) (* z1 10^m) z0)))))

(karatsuba 1234567890 9876543210)
;; ⇒ 12193263111263526900
```

### 34.4 최대 부분합(Kadane은 DP, 분할정복은 다음)

```scheme
(define (max-subarray v lo hi)
  (cond ((= lo hi) (vector-ref v lo))
        (else
         (let* ((mid (quotient (+ lo hi) 2))
                (left  (max-subarray v lo mid))
                (right (max-subarray v (+ mid 1) hi))
                (cross (max-cross v lo mid hi)))
           (max left right cross)))))

(define (max-cross v lo mid hi)
  (let loop1 ((i mid) (s 0) (best (vector-ref v mid)))
    (let ((s (+ s (vector-ref v i))))
      (let ((best (if (> s best) s best)))
        (if (= i lo)
            (let loop2 ((j (+ mid 1)) (s 0) (best2 (vector-ref v (+ mid 1))))
              (let ((s (+ s (vector-ref v j))))
                (let ((best2 (if (> s best2) s best2)))
                  (if (= j hi) (+ best best2)
                      (loop2 (+ j 1) s best2)))))
            (loop1 (- i 1) s best))))))

(define A #(-2 1 -3 4 -1 2 1 -5 4))
(max-subarray A 0 (- (vector-length A) 1))   ;; ⇒ 6   ; (4 -1 2 1)
```

### 34.5 가까운 두 점

(생략 — 연습문제로 두 차원 평면에서 도전.)

### 34.6 연습문제

1. *최대값/최소값*을 한 번의 분할정복으로 — 비교 횟수 ⌈3n/2⌉-2.
2. 행렬 거듭제곱으로 *피보나치 O(log n)*.
3. *역위(inversion)* 개수 세기 — 머지 정렬 변형.
4. 가까운 두 점(2D) 분할 정복.

\newpage

## 35장 동적 계획법

### 35.1 메모이제이션 vs 표(table) 채우기

DP는 *겹치는 부분문제*를 한 번만 풀어 결과를 저장한다.

#### 메모이제이션(top-down)

```scheme
(define memo (make-vector 100 #f))

(define (fib n)
  (cond ((< n 2) n)
        ((vector-ref memo n))
        (else
         (let ((r (+ (fib (- n 1)) (fib (- n 2)))))
           (vector-set! memo n r)
           r))))

(fib 50)   ;; ⇒ 12586269025
```

#### 표 채우기(bottom-up)

```scheme
(define (fib-tab n)
  (let ((t (make-vector (+ n 1) 0)))
    (vector-set! t 1 1)
    (do ((i 2 (+ i 1))) ((> i n) (vector-ref t n))
      (vector-set! t i (+ (vector-ref t (- i 1)) (vector-ref t (- i 2)))))))
```

### 35.2 거스름돈 — 최소 동전 수

```scheme
(define (min-coins coins amt)
  (let ((dp (make-vector (+ amt 1) +inf.0)))
    (vector-set! dp 0 0)
    (do ((a 1 (+ a 1))) ((> a amt) (vector-ref dp amt))
      (for-each
       (lambda (c)
         (when (and (>= a c)
                    (< (+ (vector-ref dp (- a c)) 1) (vector-ref dp a)))
           (vector-set! dp a (+ (vector-ref dp (- a c)) 1))))
       coins))))

(min-coins '(1 2 5) 11)   ;; ⇒ 3.0  (5+5+1)
(min-coins '(2) 3)        ;; ⇒ +inf.0
```

### 35.3 LIS(최장 증가 부분수열)

```scheme
(define (lis v)
  (let* ((n (vector-length v))
         (dp (make-vector n 1)))
    (do ((i 1 (+ i 1))) ((= i n))
      (do ((j 0 (+ j 1))) ((= j i))
        (when (and (< (vector-ref v j) (vector-ref v i))
                   (>= (vector-ref dp j) (vector-ref dp i)))
          (vector-set! dp i (+ (vector-ref dp j) 1)))))
    (let loop ((i 0) (m 0))
      (if (= i n) m
          (loop (+ i 1) (max m (vector-ref dp i)))))))

(lis #(10 9 2 5 3 7 101 18))   ;; ⇒ 4
```

O(n²). O(n log n) 버전은 이분 검색 응용 — 연습문제.

### 35.4 LCS(최장 공통 부분수열)

```scheme
(define (lcs a b)
  (let* ((m (string-length a)) (n (string-length b))
         (dp (make-vector (* (+ m 1) (+ n 1)) 0)))
    (define (idx i j) (+ (* i (+ n 1)) j))
    (do ((i 1 (+ i 1))) ((> i m))
      (do ((j 1 (+ j 1))) ((> j n))
        (vector-set! dp (idx i j)
          (if (char=? (string-ref a (- i 1)) (string-ref b (- j 1)))
              (+ (vector-ref dp (idx (- i 1) (- j 1))) 1)
              (max (vector-ref dp (idx (- i 1) j))
                   (vector-ref dp (idx i (- j 1))))))))
    (vector-ref dp (idx m n))))

(lcs "ABCBDAB" "BDCABA")   ;; ⇒ 4
```

### 35.5 0/1 배낭

```scheme
(define (knapsack01 ws vs W)
  (let* ((n (length ws))
         (ws (list->vector ws))
         (vs (list->vector vs))
         (dp (make-vector (* (+ n 1) (+ W 1)) 0)))
    (define (idx i w) (+ (* i (+ W 1)) w))
    (do ((i 1 (+ i 1))) ((> i n) (vector-ref dp (idx n W)))
      (do ((w 0 (+ w 1))) ((> w W))
        (vector-set! dp (idx i w)
          (if (>= w (vector-ref ws (- i 1)))
              (max (vector-ref dp (idx (- i 1) w))
                   (+ (vector-ref vs (- i 1))
                      (vector-ref dp (idx (- i 1) (- w (vector-ref ws (- i 1)))))))
              (vector-ref dp (idx (- i 1) w))))))))

(knapsack01 '(2 3 4 5) '(3 4 5 6) 5)   ;; ⇒ 7
```

### 35.6 편집 거리

```scheme
(define (edit-distance a b)
  (let* ((m (string-length a)) (n (string-length b))
         (dp (make-vector (* (+ m 1) (+ n 1)) 0)))
    (define (idx i j) (+ (* i (+ n 1)) j))
    (do ((i 0 (+ i 1))) ((> i m)) (vector-set! dp (idx i 0) i))
    (do ((j 0 (+ j 1))) ((> j n)) (vector-set! dp (idx 0 j) j))
    (do ((i 1 (+ i 1))) ((> i m) (vector-ref dp (idx m n)))
      (do ((j 1 (+ j 1))) ((> j n))
        (vector-set! dp (idx i j)
          (if (char=? (string-ref a (- i 1)) (string-ref b (- j 1)))
              (vector-ref dp (idx (- i 1) (- j 1)))
              (+ 1 (min (vector-ref dp (idx (- i 1) j))
                        (vector-ref dp (idx i (- j 1)))
                        (vector-ref dp (idx (- i 1) (- j 1))))))))))) 

(edit-distance "kitten" "sitting")   ;; ⇒ 3
```

### 35.7 일반 메모이제이션 매크로

```scheme
(define (memoize f)
  (let ((cache (make-hash-table)))
    (lambda args
      (cond ((ht-ref cache args) => (lambda (v) v))
            (else
             (let ((r (apply f args)))
               (ht-set! cache args r)
               r))))))
```

(`make-hash-table`은 24장 미니 구현 또는 처리계 라이브러리.)

### 35.8 연습문제

1. *Catalan 수* DP.
2. *행렬 곱 순서* DP — 최소 곱셈.
3. *LIS* O(n log n) 버전.
4. *연쇄 동전 게임* — 두 명이 양 끝에서 골라가는 최적 점수.

\newpage

## 36장 그리디

### 36.1 활동 선택

```scheme
(define (activity-selection acts)
  ;; acts: ((start . end) ...)
  (let ((sorted (sort (lambda (a b) (< (cdr a) (cdr b))) acts)))
    (let loop ((rest sorted) (last-end -inf.0) (acc '()))
      (cond ((null? rest) (reverse acc))
            ((>= (caar rest) last-end)
             (loop (cdr rest) (cdar rest) (cons (car rest) acc)))
            (else (loop (cdr rest) last-end acc))))))

(activity-selection '((1 . 4) (3 . 5) (0 . 6) (5 . 7) (8 . 9) (5 . 9)))
;; ⇒ ((1 . 4) (5 . 7) (8 . 9))
```

### 36.2 동전 거스름돈(특수 동전계)

US 동전(1,5,10,25)에서는 그리디가 *최적*. 일반 동전계에서는 DP(35.2) 필요.

```scheme
(define (greedy-coins coins amt)
  (let loop ((coins (sort > coins)) (amt amt) (acc '()))
    (cond ((zero? amt) (reverse acc))
          ((null? coins) (error "impossible"))
          ((>= amt (car coins))
           (loop coins (- amt (car coins)) (cons (car coins) acc)))
          (else (loop (cdr coins) amt acc)))))

(greedy-coins '(1 5 10 25) 67)
;; ⇒ (25 25 10 5 1 1)
```

### 36.3 허프만 코딩

빈도 기반 가변 길이 코딩.

```scheme
(define (huffman freqs)
  ;; freqs: ((sym . freq) ...)
  ;; 노드: (freq leaf-or-internal ...)
  ;;   leaf:     (freq 'leaf sym)
  ;;   internal: (freq 'int  left right)
  (let ((pq (sort (lambda (a b) (< (car a) (car b)))
                  (map (lambda (p) (list (cdr p) 'leaf (car p))) freqs))))
    (let loop ((pq pq))
      (if (null? (cdr pq)) (car pq)
          (let* ((a (car pq)) (b (cadr pq)) (rest (cddr pq))
                 (merged (list (+ (car a) (car b)) 'int a b)))
            (loop (sort (lambda (x y) (< (car x) (car y)))
                        (cons merged rest))))))))

(define (huffman-codes tree)
  (let walk ((t tree) (path '()) (acc '()))
    (case (cadr t)
      ((leaf) (cons (cons (caddr t) (reverse path)) acc))
      ((int)
       (let ((acc1 (walk (caddr t) (cons 0 path) acc)))
         (walk (cadddr t) (cons 1 path) acc1))))))

(huffman-codes (huffman '((a . 5) (b . 9) (c . 12) (d . 13) (e . 16) (f . 45))))
```

(실제 힙(28장)을 쓰면 O(n log n)로 더 효율적.)

### 36.4 작업 스케줄링(마감일·이익)

```scheme
(define (job-schedule jobs)
  ;; jobs: ((id deadline profit) ...)
  (let ((sorted (sort (lambda (a b) (> (caddr a) (caddr b))) jobs)))
    (let* ((max-d (apply max (map cadr jobs)))
           (slots (make-vector (+ max-d 1) #f)))
      (let loop ((rest sorted) (acc '()))
        (cond ((null? rest) (reverse acc))
              (else
               (let ((j (car rest)))
                 (let try ((t (cadr j)))
                   (cond ((zero? t) (loop (cdr rest) acc))
                         ((not (vector-ref slots t))
                          (vector-set! slots t (car j))
                          (loop (cdr rest) (cons (car j) acc)))
                         (else (try (- t 1))))))))))))

(job-schedule '((a 4 20) (b 1 10) (c 1 40) (d 1 30)))
;; ⇒ (c a)  ; 또는 처리 순서에 따라
```

### 36.5 연습문제

1. *분할 가능 배낭*(나눠 담을 수 있는) — 그리디로 최적.
2. *플랫폼 수 최소화*(역에 들어오는 기차 일정).
3. *Gas station* 문제.

\newpage

## 37장 백트래킹

### 37.1 패러다임

부분 해를 차근차근 만들면서, 더 나아갈 수 없으면 *되돌아*간다.

### 37.2 N-퀸

```scheme
(define (n-queens n)
  (let ((sols '()))
    (let solve ((row 0) (cols '()) (d1 '()) (d2 '()))
      (if (= row n)
          (set! sols (cons (reverse cols) sols))
          (do ((c 0 (+ c 1))) ((= c n))
            (unless (or (memv c cols)
                        (memv (+ row c) d1)
                        (memv (- row c) d2))
              (solve (+ row 1)
                     (cons c cols)
                     (cons (+ row c) d1)
                     (cons (- row c) d2))))))
    sols))

(length (n-queens 8))    ;; ⇒ 92
```

### 37.3 미로 풀기

```scheme
(define (solve-maze maze sx sy ex ey)
  (let* ((rows (vector-length maze))
         (cols (vector-length (vector-ref maze 0)))
         (visited (make-vector rows #f)))
    (do ((i 0 (+ i 1))) ((= i rows))
      (vector-set! visited i (make-vector cols #f)))
    (let walk ((x sx) (y sy) (path '()))
      (cond ((or (< x 0) (>= x rows) (< y 0) (>= y cols)) #f)
            ((vector-ref (vector-ref maze x) y) #f)            ; 벽
            ((vector-ref (vector-ref visited x) y) #f)
            ((and (= x ex) (= y ey)) (reverse (cons (cons x y) path)))
            (else
             (vector-set! (vector-ref visited x) y #t)
             (or (walk (+ x 1) y (cons (cons x y) path))
                 (walk (- x 1) y (cons (cons x y) path))
                 (walk x (+ y 1) (cons (cons x y) path))
                 (walk x (- y 1) (cons (cons x y) path))))))))
```

### 37.4 부분집합 합

```scheme
(define (subset-sum xs target)
  (let solve ((xs xs) (acc '()) (rem target))
    (cond ((zero? rem) (list (reverse acc)))
          ((null? xs) '())
          (else
           (append
            (solve (cdr xs) acc rem)
            (if (>= rem (car xs))
                (solve (cdr xs) (cons (car xs) acc) (- rem (car xs)))
                '()))))))

(subset-sum '(2 3 5 7) 10)
;; ⇒ ((3 7) (2 3 5))
```

### 37.5 순열·조합

```scheme
(define (permutations xs)
  (cond ((null? xs) '(()))
        (else
         (apply append
           (map (lambda (x)
                  (map (lambda (p) (cons x p))
                       (permutations (remove-once x xs))))
                xs)))))

(define (remove-once x xs)
  (cond ((null? xs) '())
        ((equal? (car xs) x) (cdr xs))
        (else (cons (car xs) (remove-once x (cdr xs))))))

(permutations '(1 2 3))
;; ⇒ ((1 2 3) (1 3 2) (2 1 3) (2 3 1) (3 1 2) (3 2 1))

(define (combinations xs k)
  (cond ((zero? k) '(()))
        ((null? xs) '())
        (else
         (append
          (map (lambda (c) (cons (car xs) c)) (combinations (cdr xs) (- k 1)))
          (combinations (cdr xs) k)))))

(combinations '(a b c d) 2)
;; ⇒ ((a b) (a c) (a d) (b c) (b d) (c d))
```

### 37.6 연습문제

1. *스도쿠* 풀이.
2. *단어 사다리* (BFS도 OK).
3. *그래프 색칠*(K색).
4. *기사의 여행*(체스판).

\newpage

## 38장 그래프 알고리즘

### 38.1 BFS

```scheme
(define (bfs g start)
  (let ((visited '())
        (q (make-queue)))
    (q-push! q start)
    (set! visited (cons start visited))
    (let loop ((order '()))
      (if (q-empty? q)
          (reverse order)
          (let ((v (q-pop! q)))
            (for-each
              (lambda (u)
                (unless (memq u visited)
                  (set! visited (cons u visited))
                  (q-push! q u)))
              (neighbors g v))
            (loop (cons v order)))))))

(bfs '((a . (b c)) (b . (a d)) (c . (a d)) (d . (b c e)) (e . (d))) 'a)
;; ⇒ (a b c d e)
```

### 38.2 DFS

```scheme
(define (dfs g start)
  (let ((visited '()))
    (let visit ((v start))
      (unless (memq v visited)
        (set! visited (cons v visited))
        (for-each visit (neighbors g v))))
    (reverse visited)))
```

### 38.3 최단거리 — Dijkstra

```scheme
(define (dijkstra g start)
  (let ((dist (make-hash-table))
        (visited (make-hash-table)))
    (ht-set! dist start 0)
    (let loop ()
      (let ((u (let ((best #f) (bd +inf.0))
                 (for-each
                  (lambda (e)
                    (let ((v (car e)))
                      (unless (ht-ref visited v)
                        (let ((d (or (ht-ref dist v) +inf.0)))
                          (when (< d bd)
                            (set! best v) (set! bd d))))))
                  g)
                 best)))
        (when u
          (ht-set! visited u #t)
          (for-each
            (lambda (vw)
              (let* ((v (car vw)) (w (cdr vw))
                     (alt (+ (ht-ref dist u) w))
                     (cur (or (ht-ref dist v) +inf.0)))
                (when (< alt cur) (ht-set! dist v alt))))
            (w-neighbors g u))
          (loop))))
    dist))
```

(이는 O(V²) 단순 버전. 우선순위 큐(28장)로 O((V+E) log V).)

### 38.4 최단거리 — Floyd-Warshall

모든 쌍.

```scheme
(define (floyd n adj)
  ;; adj: 인접 행렬 (없으면 +inf.0)
  (let ((d (make-matrix n n +inf.0)))
    (do ((i 0 (+ i 1))) ((= i n))
      (mat-set! d i i 0)
      (do ((j 0 (+ j 1))) ((= j n))
        (let ((w (mat-ref adj i j)))
          (when (not (eqv? w +inf.0)) (mat-set! d i j w)))))
    (do ((k 0 (+ k 1))) ((= k n) d)
      (do ((i 0 (+ i 1))) ((= i n))
        (do ((j 0 (+ j 1))) ((= j n))
          (let ((alt (+ (mat-ref d i k) (mat-ref d k j))))
            (when (< alt (mat-ref d i j))
              (mat-set! d i j alt))))))))
```

O(V³).

### 38.5 위상 정렬

```scheme
(define (topo-sort g)
  ;; g: ((u . (v ...)) ...)
  (let ((indeg (make-hash-table))
        (q '()))
    ;; 진입 차수
    (for-each
      (lambda (e) (ht-set! indeg (car e) 0)) g)
    (for-each
      (lambda (e)
        (for-each
          (lambda (v)
            (ht-set! indeg v (+ 1 (or (ht-ref indeg v) 0))))
          (cdr e)))
      g)
    ;; 큐 초기화
    (for-each
      (lambda (e)
        (when (zero? (or (ht-ref indeg (car e)) 0))
          (set! q (cons (car e) q))))
      g)
    (let loop ((q q) (acc '()))
      (cond ((null? q) (reverse acc))
            (else
             (let ((u (car q)))
               (let ((nq (cdr q)))
                 (for-each
                   (lambda (v)
                     (ht-set! indeg v (- (ht-ref indeg v) 1))
                     (when (zero? (ht-ref indeg v))
                       (set! nq (cons v nq))))
                   (or (cdr (assq u g)) '()))
                 (loop nq (cons u acc)))))))))

(topo-sort '((a . (b c)) (b . (d)) (c . (d)) (d . ())))
;; ⇒ (a c b d)  (가능한 답 중 하나)
```

### 38.6 최소 신장 트리 — Kruskal (Union-Find)

```scheme
;; Union-Find
(define (make-uf n)
  (let ((p (make-vector n 0)))
    (do ((i 0 (+ i 1))) ((= i n) p)
      (vector-set! p i i))))

(define (uf-find uf i)
  (let ((p (vector-ref uf i)))
    (if (= p i) i
        (let ((r (uf-find uf p)))
          (vector-set! uf i r)
          r))))

(define (uf-union! uf i j)
  (let ((ri (uf-find uf i)) (rj (uf-find uf j)))
    (cond ((= ri rj) #f)
          (else (vector-set! uf ri rj) #t))))

;; Kruskal
(define (kruskal n edges)
  ;; edges: ((u v w) ...)
  (let ((sorted (sort (lambda (a b) (< (caddr a) (caddr b))) edges))
        (uf (make-uf n)))
    (let loop ((es sorted) (mst '()) (cnt 0))
      (cond ((or (null? es) (= cnt (- n 1))) (reverse mst))
            (else
             (let ((e (car es)))
               (if (uf-union! uf (car e) (cadr e))
                   (loop (cdr es) (cons e mst) (+ cnt 1))
                   (loop (cdr es) mst cnt))))))))

(kruskal 4 '((0 1 1) (0 2 4) (1 2 2) (1 3 5) (2 3 3)))
;; ⇒ ((0 1 1) (1 2 2) (2 3 3))
```

### 38.7 연결 요소

```scheme
(define (connected-components g)
  (let ((seen '()) (groups '()))
    (for-each
      (lambda (e)
        (unless (memq (car e) seen)
          (let ((c (dfs g (car e))))
            (set! seen (append c seen))
            (set! groups (cons c groups)))))
      g)
    groups))
```

### 38.8 연습문제

1. *이분 그래프 판정*(BFS 색칠).
2. *Bellman-Ford* — 음의 가중치 허용 단일 출발점.
3. *Tarjan SCC* (강연결요소).
4. *A\* 검색* — 휴리스틱 함수 인자.

\newpage

## 39장 문자열 알고리즘

### 39.1 KMP — 패턴 매칭

```scheme
(define (kmp-failure pat)
  (let* ((m (string-length pat))
         (f (make-vector m 0)))
    (let loop ((i 1) (k 0))
      (cond ((= i m) f)
            ((char=? (string-ref pat i) (string-ref pat k))
             (vector-set! f i (+ k 1))
             (loop (+ i 1) (+ k 1)))
            ((> k 0) (loop i (vector-ref f (- k 1))))
            (else (vector-set! f i 0) (loop (+ i 1) 0))))))

(define (kmp-search text pat)
  (let* ((n (string-length text)) (m (string-length pat))
         (f (kmp-failure pat)))
    (let loop ((i 0) (j 0) (hits '()))
      (cond ((= i n) (reverse hits))
            ((char=? (string-ref text i) (string-ref pat j))
             (cond ((= (+ j 1) m)
                    (loop (+ i 1)
                          (vector-ref f (- m 1))
                          (cons (- i m -1) hits)))
                   (else (loop (+ i 1) (+ j 1) hits))))
            ((> j 0) (loop i (vector-ref f (- j 1)) hits))
            (else (loop (+ i 1) 0 hits))))))

(kmp-search "abracadabra" "abra")    ;; ⇒ (0 7)
```

### 39.2 라빈-카프

```scheme
(define BASE 257)
(define MOD 1000000007)

(define (poly-hash s start len)
  (let loop ((i 0) (h 0))
    (if (= i len) h
        (loop (+ i 1)
              (modulo (+ (* h BASE) (char->integer (string-ref s (+ start i))))
                      MOD)))))

(define (rabin-karp text pat)
  (let* ((n (string-length text)) (m (string-length pat))
         (ph (poly-hash pat 0 m))
         (high (let loop ((i 0) (h 1))
                 (if (= i (- m 1)) h
                     (loop (+ i 1) (modulo (* h BASE) MOD))))))
    (if (> m n) '()
        (let loop ((i 0) (h (poly-hash text 0 m)) (hits '()))
          (cond ((= i (- n m -1)) (reverse hits))
                (else
                 (let ((hits (if (and (= h ph)
                                      (string=? (substring text i (+ i m)) pat))
                                 (cons i hits) hits)))
                   (if (= i (- n m)) (loop (+ i 1) h hits)
                       (let* ((dropped (char->integer (string-ref text i)))
                              (added (char->integer (string-ref text (+ i m))))
                              (h2 (modulo (- h (* dropped high)) MOD))
                              (h3 (modulo (+ (* h2 BASE) added) MOD))
                              (h3 (if (negative? h3) (+ h3 MOD) h3)))
                         (loop (+ i 1) h3 hits))))))))))

(rabin-karp "hello world hello" "hello")   ;; ⇒ (0 12)
```

### 39.3 트라이(Trie)

```scheme
(define (trie-make) (cons #f '()))   ; (terminal? . children-alist)

(define (trie-insert! t s)
  (let loop ((node t) (i 0))
    (cond ((= i (string-length s))
           (set-car! node #t))
          (else
           (let* ((c (string-ref s i))
                  (cell (assv c (cdr node))))
             (cond (cell (loop (cdr cell) (+ i 1)))
                   (else
                    (let ((new (cons #f '())))
                      (set-cdr! node (cons (cons c new) (cdr node)))
                      (loop new (+ i 1))))))))))

(define (trie-contains? t s)
  (let loop ((node t) (i 0))
    (cond ((= i (string-length s)) (car node))
          (else
           (cond ((assv (string-ref s i) (cdr node))
                  => (lambda (cell) (loop (cdr cell) (+ i 1))))
                 (else #f))))))

(define T (trie-make))
(trie-insert! T "apple")
(trie-insert! T "app")
(trie-insert! T "ape")
(trie-contains? T "app")        ;; ⇒ #t
(trie-contains? T "appl")       ;; ⇒ #f
(trie-contains? T "apple")      ;; ⇒ #t
```

### 39.4 Z-알고리즘

```scheme
(define (z-array s)
  (let* ((n (string-length s))
         (z (make-vector n 0)))
    (vector-set! z 0 n)
    (let loop ((i 1) (l 0) (r 0))
      (cond ((= i n) z)
            (else
             (let ((k (if (< i r) (min (- r i) (vector-ref z (- i l))) 0)))
               (let extend ((k k))
                 (if (and (< (+ i k) n)
                          (char=? (string-ref s k) (string-ref s (+ i k))))
                     (extend (+ k 1))
                     (begin
                       (vector-set! z i k)
                       (if (> (+ i k) r)
                           (loop (+ i 1) i (+ i k))
                           (loop (+ i 1) l r)))))))))))

(z-array "aabcaab")
;; ⇒ #(7 1 0 0 3 1 0)
```

### 39.5 연습문제

1. *Boyer-Moore*(나쁜 문자, 좋은 접미사 규칙).
2. 트라이로 *접두사 자동완성*.
3. *Aho-Corasick* — 다중 패턴.
4. *접미 배열*(suffix array)로 부분문자열 검색.

\newpage

## 40장 수치·확률 알고리즘

### 40.1 빠른 거듭제곱 모듈러

```scheme
(define (mod-pow b e m)
  (let loop ((b (modulo b m)) (e e) (acc 1))
    (cond ((zero? e) acc)
          ((odd? e) (loop (modulo (* b b) m) (quotient e 2) (modulo (* acc b) m)))
          (else (loop (modulo (* b b) m) (quotient e 2) acc)))))

(mod-pow 2 100 1000000007)   ;; ⇒ 976371285
```

### 40.2 밀러-라빈 소수 판정

```scheme
(define (miller-rabin n . witnesses)
  (cond ((or (< n 2) (and (even? n) (> n 2))) #f)
        ((= n 2) #t)
        (else
         (let-values (((d s)
                       (let loop ((d (- n 1)) (s 0))
                         (if (odd? d) (values d s)
                             (loop (quotient d 2) (+ s 1))))))
           (let test-witness ((ws (if (null? witnesses) '(2 3 5 7 11 13)
                                      witnesses)))
             (cond ((null? ws) #t)
                   (else
                    (let* ((a (car ws))
                           (x (mod-pow a d n)))
                      (cond ((or (= x 1) (= x (- n 1)))
                             (test-witness (cdr ws)))
                           (else
                            (let r-loop ((i 1) (x x))
                              (cond ((= i s) #f)
                                    (else
                                     (let ((x (mod-pow x 2 n)))
                                       (cond ((= x (- n 1))
                                              (test-witness (cdr ws)))
                                             (else (r-loop (+ i 1) x)))))))))))))))))

(miller-rabin 100000007)    ;; ⇒ #t
(miller-rabin 100000008)    ;; ⇒ #f
```

### 40.3 가우스 적분(몬테카를로)

```scheme
(define (monte-carlo-pi n)
  (let loop ((i 0) (hits 0))
    (cond ((= i n) (* 4.0 (/ hits n)))
          (else
           (let ((x (- (* 2 (random)) 1))
                 (y (- (* 2 (random)) 1)))
             (loop (+ i 1)
                   (if (<= (+ (* x x) (* y y)) 1) (+ hits 1) hits)))))))

(monte-carlo-pi 100000)   ;; ⇒ 약 3.14...
```

(`random`은 처리계 의존. R7RS-large `(scheme random)`나 SRFI-27.)

### 40.4 GCD·확장 GCD

```scheme
(define (egcd a b)
  ;; ax + by = gcd 의 (g x y)
  (if (zero? b) (values a 1 0)
      (let-values (((g x1 y1) (egcd b (modulo a b))))
        (values g y1 (- x1 (* (quotient a b) y1))))))

(let-values (((g x y) (egcd 30 18)))
  (list g x y))
;; ⇒ (6 -1 2)   ; 30*(-1) + 18*2 = 6
```

### 40.5 모듈러 역원

```scheme
(define (mod-inv a m)
  (let-values (((g x _) (egcd a m)))
    (if (= g 1) (modulo x m) #f)))

(mod-inv 3 11)    ;; ⇒ 4   (3·4 mod 11 = 12 mod 11 = 1)
```

### 40.6 통계

```scheme
(define (mean xs) (/ (apply + xs) (length xs)))

(define (variance xs)
  (let ((m (mean xs)))
    (/ (apply + (map (lambda (x) (let ((d (- x m))) (* d d))) xs))
       (length xs))))

(define (stddev xs) (sqrt (variance xs)))
```

### 40.7 셔플 — Fisher-Yates

```scheme
(define (shuffle! v)
  (let loop ((i (- (vector-length v) 1)))
    (when (> i 0)
      (let ((j (random (+ i 1))))
        (let ((t (vector-ref v i)))
          (vector-set! v i (vector-ref v j))
          (vector-set! v j t)))
      (loop (- i 1))))
  v)
```

### 40.8 연습문제

1. 에라토스테네스의 체로 N 이하 소수.
2. 행렬 거듭제곱으로 *피보나치 O(log n)*.
3. *FFT* 개요와 다항식 곱.
4. *수치 적분*(심슨 1/3 법칙).
5. 마르코프 체인 시뮬레이션.

\newpage
# 부록

\newpage

## 부록 A — R7RS-small 표준 절차 색인

### 수치

```
+ - * /  abs  min  max  modulo  quotient  remainder
gcd  lcm  expt  sqrt  exp  log  sin  cos  tan  asin  acos  atan
floor  ceiling  truncate  round
zero?  positive?  negative?  odd?  even?
=  <  >  <=  >=
exact  inexact  exact?  inexact?
exact->inexact  inexact->exact
number->string  string->number
```

### 페어와 리스트

```
cons  car  cdr  pair?  null?  list?
list  length  reverse  append  list-tail  list-ref
member  memq  memv  assoc  assq  assv
caar  cadr  caaar ... cdddr
map  for-each  apply
```

### 문자

```
char?  char=?  char<?  char>?  char<=?  char>=?
char-alphabetic?  char-numeric?  char-whitespace?
char-upper-case?  char-lower-case?
char-upcase  char-downcase
char->integer  integer->char
```

### 문자열

```
string?  make-string  string  string-length  string-ref
string=?  string<?  string>?  string<=?  string>=?
string-ci=?  string-upcase  string-downcase
substring  string-copy  string-copy!
string-append  string->list  list->string
string-fill!  string-set!
string->symbol  symbol->string
```

### 벡터

```
vector?  make-vector  vector  vector-length  vector-ref  vector-set!
vector->list  list->vector  vector-fill!
vector-copy  vector-copy!  vector-map  vector-for-each
```

### 제어

```
procedure?  apply
map  for-each
call-with-current-continuation  call/cc
values  call-with-values
dynamic-wind
```

### I/O

```
read  write  display  newline  write-char  write-string
read-char  peek-char  read-line  read-string
eof-object?  eof-object
input-port?  output-port?
current-input-port  current-output-port  current-error-port
open-input-file  open-output-file
open-input-string  open-output-string  get-output-string
close-port  close-input-port  close-output-port
with-input-from-file  with-output-to-file
call-with-input-file  call-with-output-file
```

### 평가·예외

```
eval  apply  error  raise  raise-continuable  with-exception-handler
guard  error-object?  error-object-message  error-object-irritants
```

### 라이브러리·매크로

```
define  define-syntax  define-record-type
let  let*  letrec  letrec*  let-values  let*-values
lambda  begin  cond  case  if  when  unless  and  or  not
quote  quasiquote  unquote  unquote-splicing
syntax-rules
```

\newpage

## 부록 B — Racket과의 차이

Racket은 R7RS-small과 *대부분* 호환되지만, 기본 모드(`#lang racket`)에서는 차이가 있다.

| 항목 | R7RS | Racket(기본 모드) |
| :--- | :--- | :--- |
| `#t`/`#f` 같음 | `(eq? '() #f)` ⇒ `#f` | 동일 |
| 문자열 가변성 | 리터럴 변경 시 오류 | 동일 |
| `null` 별칭 | 없음 | `null` ≡ `'()` |
| `printf` | 없음 | 있음 |
| `define` 위치 | 본문 앞쪽만 | 어디든 |
| `lambda` 줄임 | 없음 | `(λ (x) x)` |
| 모듈 | `define-library` | `(module ... racket ...)` |
| 해시 | 처리계 의존 | `make-hash` 등 내장 |

이식성 있는 코드를 원하면 첫 줄에 `#lang r7rs` 를 두자.

\newpage

## 부록 C — 디버깅과 프로파일링

### C.1 프린트 디버깅

```scheme
(define (dbg label v) (display label) (display ": ") (write v) (newline) v)

(define (square x) (dbg 'x (* x x)))
```

`dbg`는 *값을 그대로 돌려준다* — 식 중간에 끼워 넣을 수 있다.

```scheme
(+ 1 (dbg 'half (/ x 2)))
```

### C.2 시간 측정

```scheme
(define (time-thunk thunk)
  (let ((t0 (current-jiffy)))
    (let ((r (thunk)))
      (let ((dt (/ (- (current-jiffy) t0) (jiffies-per-second))))
        (display "time: ") (display dt) (newline)
        r))))
```

### C.3 처리계별 디버거

- **DrRacket**: 단계 디버거(트레이스/스텝).
- **Chez**: `(trace 절차)` `(untrace 절차)`.
- **Geiser(Emacs)**: `M-x geiser-debug`.

### C.4 일반적 함정 체크리스트

- [ ] *오타* — `set!`을 `set`으로? `quotient`를 `quotent`로?
- [ ] *꼬리 호출이 아닌 곳에서의 깊은 재귀* — 누적자 패턴으로.
- [ ] `=` vs `equal?` — 수가 아닌 값에 `=` 쓰지 말 것.
- [ ] `'()`을 거짓으로 가정 — 참이다.
- [ ] *리터럴 변경* — 처리계가 immutable 처리 시 오류.
- [ ] `assq`로 문자열 키 — `assoc` 써야 함.
- [ ] *내부 `define`* 위치 — 본문 앞쪽만.

\newpage

## 부록 D — 더 읽을거리

### 책

- Abelson & Sussman, *Structure and Interpretation of Computer Programs*. MIT Press.
- Friedman & Felleisen, *The Little Schemer / The Seasoned Schemer*. MIT Press.
- Krishnamurthi, *Programming Languages: Application and Interpretation*. (PLAI 책)
- R. Kent Dybvig, *The Scheme Programming Language* (4th). MIT Press.
- Chris Okasaki, *Purely Functional Data Structures*. Cambridge.
- Krishnamurthi & Felleisen 외, *How to Design Programs*.

### 표준 문서

- *Revised⁷ Report on the Algorithmic Language Scheme* (R7RS-small / R7RS-large).
- *Revised⁶ Report on the Algorithmic Language Scheme* (R6RS).

### 온라인 자원

- Racket 공식 문서: docs.racket-lang.org
- Schemers.org: 표준·라이브러리 모음
- SRFI(Scheme Requests for Implementation): srfi.schemers.org

### 진로

이 책 다음 단계를 추천한다.

1. SICP 1~3장 정독 — 메타순환 평가기 만들기.
2. 자신만의 *작은 인터프리터*(Lisp 또는 Scheme 서브셋)를 구현.
3. 컴파일러 입문 — Friedman/Wand의 *Essentials of Programming Languages* 또는
   Andrew Appel의 *Modern Compiler Implementation*.
4. 함수형 자료구조 — Okasaki 책으로.

함수형 마음가짐과 Scheme의 단순성은
이후 어느 언어를 배우든 *근본을 보는 시야*가 되어준다. 즐겁게 공부하시라.

\newpage

## 색인 (Index)

```
- 가변 문자열 ............ 6.2
- 가변 페어 .............. 21.7
- 가변 인자 .............. 7.3
- 객체 (메시지 디스패치) .. 12.3
- 검색, 이분 ............. 33.2
- 검색, 선형 ............. 33.1
- 고차 함수 .............. 11
- 그래프, 인접 리스트 ..... 29.1
- 그래프, 인접 행렬 ....... 29.2
- 꼬리 호출 .............. 13
- 누적자 패턴 ............ 13.2
- 다중 값 ................ 20
- 동적 계획법 ............ 35
- 라이브러리 ............. 19
- 람다 .................. 7
- 레코드 ................. 26
- 리스트 ................. 21
- 매크로 (syntax-rules) .. 15
- 매크로 (syntax-case) ... 16
- 머지 정렬 .............. 32.4
- 메모이제이션 ........... 12.5, 35.7
- 모듈 .................. 19
- 명명된 let ............. 8.4
- 백트래킹 ............... 37
- 벡터 .................. 23
- 부적절 리스트 .......... 21.3
- 분할 정복 .............. 34
- 불변/비공개 상태 ........ 12.2
- 비교 (eq?/eqv?/equal?) . 5.7
- 빠른 거듭제곱 ........... 9.7
- 스트림 ................. 17
- 심볼 .................. 6.4
- 알고리즘 분석 ........... 31
- 알리스 (alist) .......... 22
- 예외 .................. 18
- 우선순위 큐 ............. 28
- 위생 매크로 ............. 15
- 유클리드 호제법 ......... 9.8
- 인용 (quote) ........... 3.5
- 자료구조, 트리 .......... 27
- 점근표기 ............... 31.1
- 정렬, 머지/퀵/힙 ........ 32
- 지연 평가 .............. 17
- 카운팅 정렬 ............ 32.8
- 카라추바 곱셈 ........... 34.3
- 코루틴 ................. 14.5
- 큐 .................... 30.2
- 클로저 ................. 12
- 트라이 ................. 39.3
- 트리, AVL ............... 27.5
- 트리, BST ............... 27.3
- 페어 .................. 21.1
- 평가 규칙 .............. 3.1
- 푸시다운 (Stack) ........ 30.1
- 표현식 ................. 3.1
- 함수 합성 .............. 11.5
- 해시 테이블 ............ 24
- 허프만 ................. 36.3
- 형 변환 ................ 3.3
- 환경 .................. 3.4
- 회문 .................. 6.5
- 힙 .................... 28
- 힙 정렬 ................ 28.3
- BFS ................... 38.1
- DFS ................... 38.2
- Dijkstra .............. 38.3
- Floyd-Warshall ........ 38.4
- Kruskal ............... 38.6
- KMP ................... 39.1
- LCS ................... 35.4
- LIS ................... 35.3
- N-퀸 .................. 14.7, 37.2
- Rabin-Karp ............ 39.2
- Scheme 둘러보기 ......... 1
- Z-알고리즘 ............. 39.4
```

\newpage

## 끝

이 책은 GitHub-flavored Markdown으로 작성되었으며,
`pandoc` + `xelatex`(또는 `lualatex`)로 PDF/책 인쇄용으로 변환할 수 있다.

원고에 오류·개선 제안이 있으면 알려주십시오.

— 끝
