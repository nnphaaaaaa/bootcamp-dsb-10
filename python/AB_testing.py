# import libraries
import pandas as pd
from scipy import stats

    # import dataset
df = pd.read_csv('Spotify_Tracks_Dataset.csv')

## ------------------------------------------------ ##
# 1.) เพลงที่มีเนื้อหา Explicit มีความนิยม (popularity) สูงกว่าเพลงทั่วไป?
    ## แยกกลุ่ม A (ทั่วไป) และ B (Explicit)
group_a_exp = df[df['explicit'] == False]['popularity']
group_b_exp = df[df['explicit'] == True]['popularity']

    ## คคำนวณค่าเฉลี่ยเบื้องต้น
print(f"ค่าเฉลี่ยความนิยมกลุ่ม A (ทั่วไป): {group_a_exp.mean():.2f}")
print(f"ค่าเฉลี่ยความนิยมกลุ่ม B (Explicit): {group_b_exp.mean():.2f}")

    ## ทดสอบทางสถิติ (T-Test)
t_stat, p_value = stats.ttest_ind(group_a_exp, group_b_exp)

print(f"P-Value: {p_value:.10f}")

if p_value < 0.05:
    print("ความต่างนี้ 'มีนัยสำคัญ' (เพลง Explicit ดังกว่าจริง ไม่ได้โชคช่วย)")


# เพลง Explicit ส่วนใหญ่อาจจะกระจุกตัวอยู่ในแนวเพลงที่ดังอยู่แล้ว (เช่น Hip-Hop) เลยทำให้ค่าเฉลี่ยความนิยมดูสูงขึ้น
    ## เจาะลึกรายแนวเพลง(Group by Genre)
    ## ดูว่าแต่ละแนวเพลงมีเพลง Explicit กี่เปอร์เซ็นต์
explicit_by_genre = df.groupby('track_genre')['explicit'].mean().sort_values(ascending=False)

    ## ดู 10 อันดับแรกที่มีเพลง Explicit เยอะที่สุด
print("Top 10 Genres with most Explicit content:")
print(explicit_by_genre.head(10))

    ## เลือกเฉพาะเพลงในแนว hip-hop
hip_hop_df = df[df['track_genre'] == 'hip-hop']

    ## กลุ่ม A: Hip-hop ทั่วไป
hh_normal = hip_hop_df[hip_hop_df['explicit'] == False]['popularity']

    ## กลุ่ม B: Hip-hop ที่มี Explicit
hh_explicit = hip_hop_df[hip_hop_df['explicit'] == True]['popularity']

t_stat, p_val = stats.ttest_ind(hh_normal, hh_explicit)
print(f"P-Value สำหรับกลุ่ม Hip-hop: {p_val:.4f}")

if p_val < 0.05:
    print("แม้ว่าจะอยู่ในแนวเพลงเดียวกัน เนื้อหา Explicit ก็ยังมีผลช่วยให้เพลงดังขึ้นจริง")


## ------------------------------------------------ ##
# 2. ความน่าเต้นส่งผลต่อความนิยมจริงไหม
    ## สร้างคอลัมน์ใหม่เพื่อแบ่งกลุ่มตามค่า danceability
df['dance_group'] = df['danceability'].apply(lambda x: 'High' if x >= 0.5 else 'Low')

    ## แยก popularity ของทั้งสองกลุ่มออกมา
happy_pop = df[df['dance_group'] == 'Low']['popularity']
sad_pop = df[df['dance_group'] == 'High']['popularity']

    ## คำนวณค่าเฉลี่ยเบื้องต้น
print(f"Average Popularity (Happy 😊): {happy_pop.mean():.2f}")
print(f"Average Popularity (Sad 😢): {sad_pop.mean():.2f}")

    ## ทดสอบ T-test
t_stat, p_val_dance = stats.ttest_ind(happy_pop, sad_pop)

print(f"P-Value: {p_val_dance:.10f}")

if p_val < 0.05:
    print("ความน่าเต้นส่งผลต่อความนิยมของเพลงอย่างมีนัยสำคัญ")

## ------------------------------------------------ ##
# 3. Sad vs Happy Songs: เพลงที่ฟังแล้วมีความสุข (Valence สูง) ดังกว่าเพลงเศร้าหรือเปล่า?
    ##  แบ่งกลุ่ม: Valence > 0.5 คือ Happy, นอกนั้นคือ Sad
df['mood_group'] = df['valence'].apply(lambda x: 'Happy' if x > 0.5 else 'Sad')

    ## แยกข้อมูล Popularity ออกเป็น 2 กลุ่ม
happy_pop = df[df['mood_group'] == 'Happy']['popularity']
sad_pop = df[df['mood_group'] == 'Sad']['popularity']

    ## คำนวณค่าเฉลี่ยเบื้องต้น
print(f"Average Popularity (Happy 😊): {happy_pop.mean():.2f}")
print(f"Average Popularity (Sad 😢): {sad_pop.mean():.2f}")

    ## ทดสอบทางสถิติ (T-Test)
t_stat, p_val = stats.ttest_ind(happy_pop, sad_pop)
print(f"P-Value: {p_val:.10f}")


