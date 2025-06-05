import subprocess, sys, math, random

# ---------- 0. 安裝 / 匯入 treys ----------
try:
    from treys import Card, Deck, Evaluator
except ModuleNotFoundError:
    print("treys library not found → installing ...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "treys"])
    from treys import Card, Deck, Evaluator

# ---------- 1. 參數設定 ----------
N_SIM      = 100_000      # 模擬次數
AK_SUITED  = False        # True 換成 AK 同花（As Ks）
SHOW_FIRST = False        # True 顯示第一副公共牌做 sanity-check

# ---------- 2. 固定兩手牌 ----------
hole_AK = [Card.new("As"), Card.new("Ks" if AK_SUITED else "Kd")]
hole_QQ = [Card.new("Qc"), Card.new("Qh")]

evaluator = Evaluator()
wins_AK = ties = 0

# ---------- 3. 主迴圈 ----------
for sim in range(N_SIM):
    deck = Deck()
    # 去除已發到玩家手中的 4 張牌
    for c in hole_AK + hole_QQ:
        deck.cards.remove(c)

    board = deck.draw(5)                    # 抽 5 張公共牌
    score_AK = evaluator.evaluate(board, hole_AK)
    score_QQ = evaluator.evaluate(board, hole_QQ)

    if score_AK < score_QQ:                 # 分數越小越強
        wins_AK += 1
    elif score_AK == score_QQ:
        ties += 1

    if SHOW_FIRST and sim == 0:
        print("\nSample board #1:")
        evaluator.print_cards(board)
        print("- AK hand  :", evaluator.class_to_string(
              evaluator.get_rank_class(score_AK)))
        print("- QQ hand  :", evaluator.class_to_string(
              evaluator.get_rank_class(score_QQ)))
        print()

wins_QQ = N_SIM - wins_AK - ties

# ---------- 4. 統計 ----------
p_AK_raw  = wins_AK / N_SIM
p_QQ_raw  = wins_QQ / N_SIM
p_tie     = ties / N_SIM

# 調整：平局視為各拿一半 Equity
p_AK_adj  = p_AK_raw + 0.5 * p_tie
p_QQ_adj  = p_QQ_raw + 0.5 * p_tie

# 95 % 信賴區間 (二項)
se = math.sqrt(p_AK_adj * (1 - p_AK_adj) / N_SIM)
ci_low = p_AK_adj - 1.96 * se
ci_high = p_AK_adj + 1.96 * se

# ---------- 5. 輸出 ----------
print("\n===  Monte-Carlo Result  ===")
print(f"Simulations       : {N_SIM:,}")
print(f"Player A (AK{'s' if AK_SUITED else 'o'}) vs. Player B (QQ)\n")

print(f"AK   wins : {wins_AK:7}  ({p_AK_raw:6.3%})")
print(f"QQ   wins : {wins_QQ:7}  ({p_QQ_raw:6.3%})")
print(f"Ties      : {ties:7}  ({p_tie:6.3%})")

print("\nAdjusted equity (ties split):")
print(f"  AK : {p_AK_adj*100:5.2f} %   95% CI = {ci_low*100:5.2f} – {ci_high*100:5.2f}")
print(f"  QQ : {p_QQ_adj*100:5.2f} %")