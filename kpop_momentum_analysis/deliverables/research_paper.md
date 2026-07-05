# Comeback Momentum, Chart Re-Entry, and Fandom Intensity Analysis of South Korea Top 50 Playlist

**Prepared by:** Strategy & Analytics Division, Atlantic Recording Corporation  
**Target Audience:** Atlantic Executive Leadership, Global Marketing Teams, and Industry Analysts  
**Dataset Coverage:** May 18, 2024 – November 27, 2025 (555 Days, 27,750 Cleaned Records)

---

## Abstract

South Korea’s music ecosystem is structurally distinct, driven by high-frequency promotional cycles, intense fandom streaming, and rapid chart churn. This paper analyzes Spotify South Korea Daily Top 50 playlist data to model song re-entry behaviors, measure comeback momentum, and develop a **Fandom Intensity Score** to guide release strategies. 

Our key findings reveal that:
1. **Clean content** achieves a **4x advantage** in re-entry frequency (1.91 vs. 0.45 avg re-entries) and double the chart longevity compared to explicit content.
2. **Album tracks** experience higher re-entry rates (1.71 avg re-entries) than **singles** (1.60 avg re-entries) due to deep-catalog fandom streaming, but singles achieve **39% higher longevity** (58.0 days vs. 41.7 days).
3. The K-Pop chart is highly volatile but exhibits tight re-entry cycles, with a **median chart-out gap of just 3.0 days**, illustrating that fandom reactivation is rapid and highly efficient.

---

## 1. Introduction & Market Background

Unlike Western music markets where song chart runs tend to follow a standard log-normal decay, South Korea’s music market—dominated by K-Pop—is characterized by non-linear, multi-peaked trajectories. The primary drivers of this behavior are:
- **Fandom Streaming (Streaming "Parties")**: Organized fandom networks actively stream discographies to boost rankings during comebacks, anniversaries, award seasons, and birthdays.
- **High-Frequency Comeback Cycles**: Artists release multiple mini-albums (EPs) annually, with visual concepts and promotional runs spanning 2–4 weeks.
- **"Reverse Runs" (Yeok-ju-haeng)**: Older tracks suddenly surge back onto charts due to viral variety show appearances, live performances, or social media trends.

For a global record label like Atlantic Recording Corporation, applying standard Anglo-American release strategies in South Korea leads to inefficient budget allocation and missed catalog monetization opportunities. Understanding the mechanics of comeback momentum is crucial for maximizing commercial impact.

---

## 2. Methodology & Mathematical Framework

### 2.1 Data Cleansing & Validation
The raw dataset contains daily Spotify Top 50 playlist records. An initial validation revealed:
- **Temporal Gaps**: 4 missing dates (2025-03-14, 2025-03-25, 2025-07-11, 2025-08-13).
- **Anomalous Log Entries**: March 1, 2025 contained 100 entries instead of 50.
  - *Deduplication Strategy*: We grouped duplicate entries by `(date, position)` and retained the instance with the highest popularity score.
  - *Normalization*: All text strings (songs, artists, album types) were stripped of leading/trailing whitespace, and text casing was normalized. 
  - *Conversion*: `duration_ms` was converted to minutes (`duration_min = duration_ms / 60000.0`).
  
Following cleaning, the dataset matches the structural requirement of **exactly 50 entries per day**, resulting in **27,750 validated records** across **555 unique days**.

### 2.2 Chart Run & Re-Entry Detection Algorithm
We mapped dates to a zero-indexed timeline array $T = [t_0, t_1, \dots, t_{554}]$. For a given song $S$, we extracted its set of active indices $I_S \subseteq T$. A "run" $R_k$ is a contiguous block of indices $I_{S,k} = [i_{start}, \dots, i_{end}]$ where $i_{j+1} - i_j = 1$.
- **Exit Date**: The calendar date corresponding to $i_{end}$ for run $R_k$.
- **Re-Entry Date**: The calendar date corresponding to $i_{start}$ for run $R_{k+1}$ (where $k \ge 0$).
- **Re-Entry Frequency ($F_{re}$)**: The total number of runs minus one ($N_{runs} - 1$).
- **Chart-Out Gap ($G_{days}$)**: The calendar time elapsed between runs:
  $$G_{days} = \text{Date}(i_{start, k+1}) - \text{Date}(i_{end, k})$$

### 2.3 KPI Formulations

#### A. Rank Jump Magnitude ($\Delta R$)
Measures the vertical climb of a song post-re-entry. Since rank 1 is the highest and rank 50 is the lowest:
$$\Delta R = \max(0, R_{start} - R_{peak})$$
*Where $R_{start}$ is the position on the day of re-entry, and $R_{peak}$ is the highest position achieved during that run.*

#### B. Popularity Spike Score ($\Delta P$)
Measures the absolute gain in the API popularity index during the run:
$$\Delta P = \max(0, P_{peak} - P_{start})$$

#### C. Rank Recovery Speed ($V_{rec}$)
Represents the velocity of the climb:
$$V_{rec} = \frac{\Delta R}{\max(1, D_{peak})}$$
*Where $D_{peak}$ is the number of days taken to reach the peak rank from the start of the run.*

#### D. Momentum Spike Score ($S_{mom}$)
A combined index of comeback intensity, normalized out of 100:
$$S_{mom} = \left(\frac{\Delta R}{49}\right) \times 50 + \left(\frac{\Delta P}{100}\right) \times 50$$

#### E. Fandom Intensity Proxy Score ($S_{fandom}$)
An aggregate metric representing the strength of fandom-driven engagement.
For songs with $F_{re} > 0$:
$$S_{fandom} = w_1 \cdot \min(100, F_{re} \times 25) + w_2 \cdot \min(100, \bar{S}_{mom} \times 2) + w_3 \cdot \min(100, \bar{V}_{rec} \times 10)$$
*Where weights are set at $w_1 = 0.40$ (re-entry frequency), $w_2 = 0.30$ (comeback spike score), and $w_3 = 0.30$ (recovery velocity). For songs with zero re-entries, $S_{fandom}$ is calculated at a reduced weight based on initial entry metrics.*

---

## 3. Empirical Results & Findings

Across the 555-day tracking window, the analysis engine identified **541 unique songs** by **194 artists**, generating **1,429 total chart runs** and **888 re-entries**.

### 3.1 Fandom Intensity Leaderboard
The compound $S_{fandom}$ successfully isolates tracks displaying heavy fandom-driven streaming patterns versus those with standard organic runs:

| Rank | Song Title | Artist | Re-Entries | Peak Rank | Fandom Intensity Score |
| :--- | :--- | :--- | :---: | :---: | :---: |
| 1 | **Dreamers** | Jung Kook & BTS | 4 | #10 | **69.80** |
| 2 | **Who (Acoustic Remix)** | Jimin | 4 | #18 | **67.71** |
| 3 | **Last Christmas - Single** | Wham! | 1 | #13 | **57.76** |
| 4 | **NEMONEMO** | YENA | 5 | #31 | **55.23** |
| 5 | **Memories** | RIIZE | 4 | #24 | **54.47** |

*Note on Outliers:* *Last Christmas* by Wham! emerges in the top 3 with a high fandom score. This represents a seasonal "holiday fandom" behavior, where structural annual playlisting acts similarly to organized fan streaming.

### 3.2 High-Frequency Re-Entry Catalysts
The artists with the highest absolute volume of chart re-entries demonstrate the power of specialized domestic fandoms:
1. **Lim Young Woong** (163 Total Re-entries): Known for a mature, highly dedicated fanbase that streams his entire catalog (e.g. *Our Blues, Our Life* achieved 28 separate re-entries).
2. **Jimin** (122 Total Re-entries): Driven by global and domestic BTS fan networks.
3. **NewJeans** (113 Total Re-entries): Showcasing sustained cultural relevance, with *Ditto* re-entering 26 times.

### 3.3 The Single vs. Album Track Comeback Paradox
The analysis reveals a clear trade-off between release formats:

| Metric | Album Tracks ($N=219$) | Singles ($N=321$) |
| :--- | :---: | :---: |
| **Avg. Re-entries per Song** | **1.71** | 1.60 |
| **Avg. Chart Longevity (Days)** | 41.71 | **57.99** |
| **Avg. Fandom Intensity Score** | 16.71 | **17.94** |

- **Insight**: Album tracks exhibit a higher re-entry rate (1.71 vs 1.60), reflecting that fans stream entire B-side catalogs during comeback weeks. However, singles maintain a **39% higher longevity** (58.0 vs. 41.7 days), as general public streaming eventually takes over from fandom-only pushes.

### 3.4 The Explicit Content Penalty
In South Korea, explicit songs face a severe disadvantage:

| Metric | Clean Content ($N=443$) | Explicit Content ($N=98$) |
| :--- | :---: | :---: |
| **Avg. Re-entries per Song** | **1.91** | 0.45 |
| **Avg. Chart Longevity (Days)** | **56.66** | 27.04 |
| **Avg. Fandom Intensity Score** | **19.12** | 9.66 |

- **Insight**: Clean songs obtain **4.2x more re-entries** and double the retention of explicit songs. South Korea's playlist ecosystem and cultural streaming preferences strongly filter out explicit content. Fandoms rarely sustain streaming campaigns for explicit releases.

### 3.5 Time Gap Analysis
The distribution of the **888 chart gaps** shows:
- **Mean Gap**: 9.96 days
- **Median Gap**: **3.00 days**
- **Interpretation**: A median gap of 3 days indicates that songs hovering near the bottom of the Top 50 drop out on weekdays and are immediately pushed back in during weekends or specific promotional windows. Fandom reactivation is swift and high-frequency.

---

## 4. Strategic Recommendations for Atlantic Recording Corporation

### 1. Mandate Clean Edits for South Korea Focus
Releasing explicit tracks without immediate clean alternatives severely limits chart potential. Atlantic must make clean edits the primary focus for streaming playlist pitching in South Korea. Clean versions are highly favored by local curators and domestic fans.

### 2. Implement the "Dual-Peak" Promotion Strategy
Given that album tracks experience high re-entry rates but low longevity, Atlantic should structure K-Pop campaigns around two distinct peaks:
- **Peak 1 (Initial Release)**: High-intensity promotion focusing on the lead Single to establish chart longevity.
- **Peak 2 (Fandom Re-activation)**: Re-promote B-side album tracks around Day 21–30 using fan-targeted events (anniversaries, exclusive video content, remix drops) to exploit the natural B-side re-entry momentum.

### 3. Target Catalog Re-entry during "Streaming Gaps"
With a median re-entry gap of 3 days, there is a constant churn at the bottom of the Top 50. Atlantic should schedule catalog activations (such as TikTok challenges or anniversary vinyl announcements) during low-competition chart weeks to trigger fandom streaming when the re-entry threshold is lowest.

---

## 5. Conclusion
Adapting to South Korea’s music ecosystem requires moving away from traditional single-peak lifecycle modeling. By leveraging the Fandom Intensity Score and accounting for the structural preference for clean content and B-side re-entries, Atlantic Recording Corporation can optimize release timings, increase catalog monetization, and achieve sustained chart presence.
