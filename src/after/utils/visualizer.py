# utils/visualizer.py

import logging
import os

import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def visualize_evolution(stats_history, output_dir):
    """GP 진화 과정을 시각화하여 저장

    Args:
        stats_history: 세대별 통계 정보 리스트
            [{
                'generation': int,
                'max': float,
                'avg': float,
                'min': float,
                'std': float
            }, ...]
        output_dir: 저장할 디렉토리 경로
    """
    if not stats_history:
        logging.warning("⚠️ 시각화할 통계 데이터가 없습니다.")
        return

    generations = [s["generation"] for s in stats_history]
    max_fitness = [s["max"] for s in stats_history]
    avg_fitness = [s["avg"] for s in stats_history]
    min_fitness = [s["min"] for s in stats_history]
    std_fitness = [s["std"] for s in stats_history]

    # 메인 진화 과정 그래프
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=("Fitness 진화 과정", "Fitness 표준편차"),
        vertical_spacing=0.12,
        row_heights=[0.7, 0.3],
    )

    # 최고 fitness
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=max_fitness,
            mode="lines+markers",
            name="최고 Fitness",
            line=dict(color="#2ecc71", width=3),
            marker=dict(size=8),
        ),
        row=1,
        col=1,
    )

    # 평균 fitness
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=avg_fitness,
            mode="lines+markers",
            name="평균 Fitness",
            line=dict(color="#3498db", width=2),
            marker=dict(size=6),
        ),
        row=1,
        col=1,
    )

    # 최저 fitness
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=min_fitness,
            mode="lines+markers",
            name="최저 Fitness",
            line=dict(color="#e74c3c", width=2),
            marker=dict(size=6),
        ),
        row=1,
        col=1,
    )

    # 표준편차
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=std_fitness,
            mode="lines+markers",
            name="표준편차",
            line=dict(color="#9b59b6", width=2),
            marker=dict(size=6),
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # 레이아웃 설정
    fig.update_xaxes(title_text="세대", row=1, col=1)
    fig.update_xaxes(title_text="세대", row=2, col=1)
    fig.update_yaxes(title_text="Fitness", row=1, col=1)
    fig.update_yaxes(title_text="표준편차", row=2, col=1)

    fig.update_layout(
        title={
            "text": "GP 전략 최적화 진화 과정",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 24},
        },
        height=800,
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # HTML 저장 (인터랙티브)
    html_path = os.path.join(output_dir, "evolution.html")
    fig.write_html(html_path)
    logging.info(f"📈 진화 과정 시각화 (HTML) 저장 완료: '{html_path}'")

    # PNG 저장 (matplotlib 사용)
    _save_evolution_png(stats_history, output_dir)


def _save_evolution_png(stats_history, output_dir):
    """matplotlib를 사용하여 진화 과정을 PNG로 저장"""
    generations = [s["generation"] for s in stats_history]
    max_fitness = [s["max"] for s in stats_history]
    avg_fitness = [s["avg"] for s in stats_history]
    min_fitness = [s["min"] for s in stats_history]
    std_fitness = [s["std"] for s in stats_history]

    # 한글 폰트 설정
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False

    # 서브플롯 생성
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle("GP Evolution Process", fontsize=16, fontweight="bold")

    # 상단: Fitness 진화 과정
    ax1.plot(
        generations,
        max_fitness,
        "o-",
        color="#2ecc71",
        linewidth=2,
        markersize=6,
        label="Max Fitness",
    )
    ax1.plot(
        generations,
        avg_fitness,
        "s-",
        color="#3498db",
        linewidth=2,
        markersize=5,
        label="Avg Fitness",
    )
    ax1.plot(
        generations,
        min_fitness,
        "^-",
        color="#e74c3c",
        linewidth=2,
        markersize=5,
        label="Min Fitness",
    )
    ax1.set_xlabel("Generation", fontsize=12)
    ax1.set_ylabel("Fitness", fontsize=12)
    ax1.set_title("Fitness Evolution", fontsize=14)
    ax1.legend(loc="best", frameon=True, shadow=True)
    ax1.grid(True, alpha=0.3)

    # 하단: 표준편차
    ax2.plot(
        generations,
        std_fitness,
        "D-",
        color="#9b59b6",
        linewidth=2,
        markersize=5,
        label="Std Dev",
    )
    ax2.set_xlabel("Generation", fontsize=12)
    ax2.set_ylabel("Standard Deviation", fontsize=12)
    ax2.set_title("Fitness Standard Deviation", fontsize=14)
    ax2.legend(loc="best", frameon=True, shadow=True)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    # PNG 저장
    png_path = os.path.join(output_dir, "evolution.png")
    plt.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close()
    logging.info(f"📊 진화 과정 시각화 (PNG) 저장 완료: '{png_path}'")


def visualize_fitness_distribution(final_population, output_dir):
    """최종 개체군의 fitness 분포를 히스토그램으로 시각화

    Args:
        final_population: 최종 개체군 리스트
        output_dir: 저장할 디렉토리 경로
    """
    if not final_population:
        logging.warning("⚠️ 시각화할 개체군 데이터가 없습니다.")
        return

    fitness_values = [ind.fitness.values[0] for ind in final_population]

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x=fitness_values,
            nbinsx=30,
            marker=dict(color="#3498db", line=dict(color="#2c3e50", width=1)),
            name="Fitness 분포",
        )
    )

    fig.update_layout(
        title={
            "text": "최종 개체군 Fitness 분포",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20},
        },
        xaxis_title="Fitness",
        yaxis_title="개체 수",
        template="plotly_white",
        height=500,
    )

    # HTML 저장
    html_path = os.path.join(output_dir, "fitness_distribution.html")
    fig.write_html(html_path)
    logging.info(f"📊 Fitness 분포 시각화 (HTML) 저장 완료: '{html_path}'")

    # PNG 저장 (matplotlib 사용)
    _save_distribution_png(final_population, output_dir)


def _save_distribution_png(final_population, output_dir):
    """matplotlib를 사용하여 fitness 분포를 PNG로 저장"""
    fitness_values = [ind.fitness.values[0] for ind in final_population]

    plt.figure(figsize=(10, 6))
    plt.hist(fitness_values, bins=30, color="#3498db", edgecolor="#2c3e50", alpha=0.7)
    plt.xlabel("Fitness", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.title("Final Population Fitness Distribution", fontsize=14, fontweight="bold")
    plt.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()

    # PNG 저장
    png_path = os.path.join(output_dir, "fitness_distribution.png")
    plt.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close()
    logging.info(f"📊 Fitness 분포 시각화 (PNG) 저장 완료: '{png_path}'")
