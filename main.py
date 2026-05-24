import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Kendi modüllerini import et
from src.data_core import TSPEnvironment
from src.optimizer import GRASPSolver

# ---------------------------------------------------------
# SAYFA AYARLARI (Geniş mod ve Başlık)
# ---------------------------------------------------------
st.set_page_config(page_title="TSP-D Optimizer", layout="wide", page_icon="🚁")

# ---------------------------------------------------------
# GRAFİK FONKSİYONLARI (Streamlit'e Uyarlanmış Hali)
# plt.show() yerine st.pyplot() kullanıyoruz.
# ---------------------------------------------------------
def plot_iteration_graph(iterations, costs):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(iterations, costs, marker="o", color="#e74c3c")
    ax.set_title("GRASP İlerlemesi: İterasyon vs En İyi Maliyet")
    ax.set_xlabel("İterasyon")
    ax.set_ylabel("En İyi Maliyet ($)")
    ax.grid(True, linestyle=":", alpha=0.6)
    return fig

def plot_truck_vs_drone(results):
    labels = [str(r["customers"]) for r in results]
    truck_counts = [r["truck_stops"] for r in results]
    drone_counts = [r["drone_deliveries"] for r in results]

    x = range(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar([i - width / 2 for i in x], truck_counts, width=width, label="Kamyon Durakları", color="#34495e")
    ax.bar([i + width / 2 for i in x], drone_counts, width=width, label="Dron Teslimatları", color="#f39c12")
    
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_xlabel("Müşteri Sayısı")
    ax.set_ylabel("Adet")
    ax.set_title("Kamyon ve Dron Kullanım Karşılaştırması")
    ax.legend()
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    return fig

def plot_benchmark_improvement(results):
    labels = [str(r["customers"]) for r in results]
    improvements = [r["improvement"] if r["improvement"] is not None else 0 for r in results]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(labels, improvements, color="#2ecc71")
    ax.set_xlabel("Müşteri Sayısı")
    ax.set_ylabel("İyileşme (%)")
    ax.set_title("Sadece Kamyon (Baseline) Modeline Göre İyileşme Yüzdesi")
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    
    # Barların üstüne yüzdeyi yazma
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"%{yval:.1f}", ha='center', va='bottom', fontweight='bold')
    
    return fig

# ---------------------------------------------------------
# CORE ALGORİTMA ÇALIŞTIRICI
# ---------------------------------------------------------
# main.py içindeki bu fonksiyonu şununla değiştir:
def run_file_scenario(file_path, max_iterations, k_max):
    # Haritayı oluştur
    env = TSPEnvironment()
    # Rastgele değil, dosyadan yükle
    env.load_from_txt(file_path) 
    
    solver = GRASPSolver(environment=env, max_iterations=max_iterations, k_max=k_max)
    best_sol = solver.solve()

    baseline_cost = None
    improvement = None

    if solver.baseline_solution is not None:
        baseline_cost = solver.baseline_solution.total_cost
        best_cost = best_sol.total_cost
        improvement = ((baseline_cost - best_cost) / baseline_cost) * 100.0

    return {
        "env": env,
        "best_sol": best_sol,
        "baseline_cost": baseline_cost,
        "best_cost": best_sol.total_cost,
        "improvement": improvement,
        "truck_stops": len(best_sol.truck_route),
        "drone_deliveries": len(best_sol.drone_deliveries),
        "iteration_history": solver.iteration_history,
        "best_cost_history": solver.best_cost_history,
    }

# ---------------------------------------------------------
# STREAMLIT UI - ANA GÖVDE
# ---------------------------------------------------------
st.title("🚁 Dron Destekli Araç Rotalama (TSP-D) Optimizer")
st.markdown("Endüstri ve Yazılım Mühendisliği Ortak Projesi - **GRASP Algoritması**")

# YAN PANEL (SIDEBAR) - Hocaların oynamaya bayılacağı kısım
st.sidebar.header("⚙️ Parametreleri Ayarla")
num_cust = st.sidebar.slider("Müşteri Sayısı", min_value=10, max_value=200, value=50, step=10)
area_size = st.sidebar.number_input("Harita Alanı (km²)", min_value=10, max_value=1000, value=100)
max_iter = st.sidebar.slider("Maksimum İterasyon", min_value=5, max_value=2000, value=10, step=5)
k_max = st.sidebar.slider("K-Max (Multi-start)", min_value=1, max_value=10, value=4)

# ANA EKRAN SEKMELERİ
tab1, tab2 = st.tabs(["📍 Canlı Senaryo (Single Run)", "📊 Benchmark Testleri (Batch Run)"])

with tab1:
    st.subheader(f"Canlı Optimizasyon: {num_cust} Müşteri")
    
    if st.button("🚀 Algoritmayı Çalıştır (Run)", use_container_width=True):
        with st.spinner('GRASP Algoritması en iyi rotayı arıyor...'):
            res = run_single_scenario(num_cust, area_size, max_iter, k_max)
        
        st.success("Optimizasyon Tamamlandı!")
        
        # Sonuçları Metric Kartları ile Göster
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Kamyon (Baseline) Maliyet", f"${res['baseline_cost']:.2f}" if res['baseline_cost'] else "N/A")
        col2.metric("TSP-D (Sizin) Maliyet", f"${res['best_cost']:.2f}", delta=f"%{res['improvement']:.1f} Kazanç")
        col3.metric("Kamyon Teslimatı", f"{res['truck_stops']} Müşteri")
        col4.metric("Dron Teslimatı", f"{res['drone_deliveries']} Müşteri")

        st.divider()
        
        # Grafikleri yan yana yerleştir
        col_map, col_chart = st.columns([3, 2])
        
        with col_map:
            st.markdown("#### 🗺️ Final Rota Haritası")
            # NOT: Kendi yazdığın plot_solution() fonksiyonu plt.show() yapıyorsa, 
            # Streamlit'te görünmesi için kodunu fig döndürecek şekilde ufak revize etmelisin. 
            # Eğer fig döndürüyorsa: st.pyplot(res['env'].plot_solution(res['best_sol']))
            st.pyplot(res['env'].plot_solution(res['best_sol'])) 

        with col_chart:
            st.markdown("#### 📉 İterasyon İlerlemesi")
            fig_iter = plot_iteration_graph(res["iteration_history"], res["best_cost_history"])
            st.pyplot(fig_iter)

with tab2:
    st.subheader("Otomatik Benchmark Karşılaştırması")
    st.markdown("Bu sekme, farklı müşteri sayıları (Örn: 50 ve 100) için algoritmayı arka arkaya koşturur ve kıyaslar.")
    
    test_nodes = st.multiselect("Test Edilecek Müşteri Sayıları:", [10, 50, 100, 150, 250], default=[50, 100])
    
    if st.button("⚡ Benchmark Başlat"):
        scenario_results = []
        progress_bar = st.progress(0)
        
        for idx, n in enumerate(test_nodes):
            with st.spinner(f"N={n} için çalışıyor..."):
                result = run_single_scenario(n, area_size=100, max_iterations=5, k_max=3) # Benchmark için hafif ayarlar
                scenario_results.append(result)
            progress_bar.progress((idx + 1) / len(test_nodes))
            
        st.success("Tüm Senaryolar Tamamlandı!")
        
        c1, c2 = st.columns(2)
        with c1:
            st.pyplot(plot_truck_vs_drone(scenario_results))
        with c2:
            st.pyplot(plot_benchmark_improvement(scenario_results))