import pygame
import sys
import time

# 1. 설정 ############################################################################
# 게임 설정
BOARD_SIZE = 19
STONE_RADIUS = 10

# 색상 설정
BACKGROUND_COLOR = (255, 206, 158)
BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
GRID_COLOR = (0, 0, 0)

# 보드 및 화면 설정
SCREEN_SIZE = (570, 570)
GRID_SIZE = SCREEN_SIZE[0] // BOARD_SIZE

# 상태 설정
EMPTY = 0
USER = 1
COMPUTER = 2

# 초기화
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("오목")

# 보드 초기화
board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]

# 각 플레이어의 시간 제한 변수 초기화
user_time = 0
computer_time = 0

# 보드 그리는 함수
def draw_board():
    screen.fill(BACKGROUND_COLOR)
    for i in range(BOARD_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, i * GRID_SIZE), (SCREEN_SIZE[0], i * GRID_SIZE))
        pygame.draw.line(screen, GRID_COLOR, (i * GRID_SIZE, 0), (i * GRID_SIZE, SCREEN_SIZE[1]))

# 돌 그리는 함수
def draw_stone(row, col, color):
    pygame.draw.circle(screen, color, (col * GRID_SIZE, row * GRID_SIZE), STONE_RADIUS)

# 돌 놓는 함수
def place_stone(row, col, player):
    if board[row][col] == EMPTY:
        board[row][col] = player
        return True
    return False
  
# 2. evaluate 함수, alpha-beta pruning #############################################################################
# 휴리스틱 함수
def heuristic(board, player):
    score = 0
    opponent = COMPUTER if player == USER else USER
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == player:
                score += evaluate_position(board, r, c, player)
            elif board[r][c] == opponent:
                score -= evaluate_position(board, r, c, opponent)
    return score

# board에서 각 위치에 대해 evaluate
def evaluate_position(board, row, col, player):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    score = 0
    for dr, dc in directions:
        count = 1
        empty_ends = 0
        r, c = row, col
        for _ in range(4):
            r, c = r + dr, c + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                if board[r][c] == player:
                    count += 1
                elif board[r][c] == EMPTY:
                    empty_ends += 1
                    break
                else:
                    break
            else:
                break
        r, c = row, col
        for _ in range(4):
            r, c = r - dr, c - dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                if board[r][c] == player:
                    count += 1
                elif board[r][c] == EMPTY:
                    empty_ends += 1
                    break
                else:
                    break
            else:
                break
        score += evaluate_count(count, empty_ends, row, col)
    return score

# player에게 점수 부여 
def evaluate_count(count, empty_ends, row, col):
    score = 0
    
    # 가운데에 있을수록 10점, 멀어질수록 0에 가까워지도록 가중치 설정 (첫 돌을 가운데에 놓게 하기위해)
    distance_from_center = abs(row - BOARD_SIZE // 2) + abs(col - BOARD_SIZE // 2)
    center_score = max(0.1, 10 - distance_from_center * 0.1)
    
    # 연속된 돌의 개수에 따라 점수 부여
    # 막혀있으면 점수 조금 낮게 줌
    if count >= 5:  # 승리 가능한 상태라면 inf 반환
        score += 10000
    elif count == 4:
        if empty_ends == 2:  # 연속된 돌 양쪽 끝이 비어있는 경우
            score += 9000
        elif empty_ends == 1:  # 한 쪽 끝이 비어있는 경우
            score +=  4500
    elif count == 3:
        if empty_ends == 2:
            return 4000
        elif empty_ends == 1:
            score += 3500
    elif count == 2:
        if empty_ends == 2:
            score += 2000
        elif empty_ends == 1:
            score+= 1500
    elif count == 1:
        if empty_ends == 2:
            score += 100
    
    score += center_score
    return score

# Alpha-Beta Pruning 함수
def alpha_beta_pruning(board, depth, alpha, beta, maximizing_player):
    if depth == 0:
        return None, heuristic(board, USER)
    
    if maximizing_player:
        max_eval = float('-inf')
        best_move = None
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] == EMPTY:
                    board[r][c] = USER
                    eval = alpha_beta_pruning(board, depth-1, alpha, beta, False)[1]
                    board[r][c] = EMPTY
                    if eval > max_eval:
                        max_eval = eval
                        best_move = (r, c)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
        return best_move, max_eval
    else:
        min_eval = float('inf')
        best_move = None
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] == EMPTY:
                    board[r][c] = COMPUTER
                    eval = alpha_beta_pruning(board, depth - 1, alpha, beta, True)[1]
                    board[r][c] = EMPTY
                    if eval < min_eval:
                        min_eval = eval
                        best_move = (r, c)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
        return best_move, min_eval


# 3. 게임 실행 코드 #########################################################################

# 승리 확인
def check_win(row, col, player):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dr, dc in directions:
        count = 1
        r, c = row, col
        for _ in range(4):
            r, c = r + dr, c + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
                count += 1
            else:
                break
        r, c = row, col
        for _ in range(4):
            r, c = r - dr, c - dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
                count += 1
            else:
                break
        if count >= 5:
            return True
    return False

# 게임 종료 함수
def game_over(winner):
    font = pygame.font.SysFont(None, 30)
    text = font.render(f"{winner} Wins!", True, BLACK_COLOR)
    text_rect = text.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    sys.exit()
    
# 시간초과됐을 때 게임종료하는 함수
def time_out(winner):
    font = pygame.font.SysFont(None, 30)
    text = font.render(f"{winner} Wins! (Time Out)", True, BLACK_COLOR)
    text_rect = text.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    sys.exit()

#main
def main():
    global user_time, computer_time
    
    # 누구의 턴인지 선택
    first_turn = input("Who's first? (computer: x / user: o) ").lower()
    if first_turn not in ['x', 'o']:
        print("Invalid input. Please choose 'x' or 'o'.")
        sys.exit()
    
    # 시간 제한 설정
    time_limit = int(input("Set time limit (0-60 seconds): "))
    if not 0 <= time_limit <= 60:
        print("Invalid time limit. Please enter a value between 0 and 60.")
        sys.exit()
    
    # 턴에 따른 색상 및 시작 플레이어 설정
    if first_turn == 'x':
        computer_color = BLACK_COLOR
        user_color = WHITE_COLOR
        turn = COMPUTER
    else:
        computer_color = WHITE_COLOR
        user_color = BLACK_COLOR
        turn = USER
    
    # 게임 실행
    game_over_flag = False
    while not game_over_flag:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # 사용자 턴
            if event.type == pygame.MOUSEBUTTONDOWN and turn == USER:
                start_time = time.time()  # 턴 시작 시간 기록
                col = event.pos[0] // GRID_SIZE
                row = event.pos[1] // GRID_SIZE
                if place_stone(row, col, USER):
                    draw_stone(row, col, user_color)
                    if check_win(row, col, USER):
                        game_over("Player")
                        game_over_flag = True
                    turn = COMPUTER
                    pygame.display.flip()
                end_time = time.time()  # 턴 종료 시간 기록
                # user_time += end_time - start_time  # 사용자의 경과 시간 누적
                # # 시간 제한 확인
                # if user_time > time_limit:
                #     time_out("Computer")
                #     game_over_flag = True
            # 컴퓨터 턴
            if turn == COMPUTER and not game_over_flag:
                start_time = time.time()  # 턴 시작 시간 기록
                move, _ = alpha_beta_pruning(board, 2, float('-inf'), float('inf'), True)
                if place_stone(move[0], move[1], COMPUTER):
                    draw_stone(move[0], move[1], computer_color)
                    if check_win(move[0], move[1], COMPUTER):
                        game_over("Computer")
                        game_over_flag = True
                    turn = USER
                    pygame.display.flip()
                end_time = time.time()  # 턴 종료 시간 기록
                # computer_time += end_time - start_time  # 컴퓨터의 경과 시간 누적
                # # 시간 제한 확인
                # if computer_time > time_limit:
                #     time_out("Player")
                #     game_over_flag = True

if __name__ == "__main__":
    draw_board()
    pygame.display.flip()
    main()
