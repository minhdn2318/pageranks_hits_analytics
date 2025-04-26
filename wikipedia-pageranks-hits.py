import networkx as nx
import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st
import matplotlib.pyplot as plt
import io
import base64

# Hàm tải và parse HTML từ URL
def get_links(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href.startswith('http'):
                links.add(href)
        return links
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi tải URL {url}: {e}")
        return set()

# Hàm xây dựng đồ thị từ một danh sách các URL
def build_graph(urls):
    G = nx.DiGraph()
    for url in urls:
        links = get_links(url)
        for link in links:
            G.add_edge(url, link)
            G.nodes[url]['url'] = url  # Gán url cho nút
            G.nodes[link]['url'] = link  # Gán url cho các nút liên kết
    return G

# Hàm phân tích HITS và trả về bảng kết quả
def analyze_hits(G):
    hits_auth, hits_hub = nx.hits(G, max_iter=100, tol=1e-6)
    
    data = {
        'Tiêu đề': [G.nodes[i]['url'] for i in G.nodes],
        'Link': [G.nodes[i]['url'] for i in G.nodes],
        'Authen': [hits_auth[i] for i in G.nodes],
        'Hub': [hits_hub[i] for i in G.nodes]
    }
    
    df = pd.DataFrame(data)
    return df.sort_values(by='Authen', ascending=False)

# Hàm phân tích PageRank và trả về bảng kết quả
def analyze_pagerank(G):
    pagerank = nx.pagerank(G, alpha=0.85)
    
    data = {
        'Tiêu đề': [G.nodes[i]['url'] for i in G.nodes],
        'Link': [G.nodes[i]['url'] for i in G.nodes],
        'PageRank': [pagerank[i] for i in G.nodes]
    }
    
    df = pd.DataFrame(data)
    return df.sort_values(by='PageRank', ascending=False)

# Hàm để tạo đồ thị và chuyển thành base64 để hiển thị trên web
def plot_graph(G):
    plt.figure(figsize=(10, 8))
    nx.draw(G, with_labels=True, font_size=8, node_size=300, node_color='lightblue')
    plt.title("Đồ thị liên kết")
    
    # Lưu đồ thị vào bộ nhớ dưới dạng base64
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
    plt.close()
    return img_base64

# Tạo giao diện Streamlit
def main():
    st.title('Phân tích HITS và PageRank từ Wikipedia')
    
    # Form nhập từ khóa và chọn thuật toán
    keyword = st.text_input('Nhập từ khóa', 'Đại học quốc gia Hà Nội')
    algorithm = st.selectbox('Chọn thuật toán', ['HITS', 'PageRank'])
    
    # Nút phân tích
    if st.button('Phân tích'):
        # Tạo URL tìm kiếm Wikipedia
        search_url = f'https://en.wikipedia.org/wiki/{keyword.replace(" ", "_")}'
        G = build_graph([search_url])
        
        # Phân tích HITS hoặc PageRank
        if algorithm == 'HITS':
            result_df = analyze_hits(G)
        elif algorithm == 'PageRank':
            result_df = analyze_pagerank(G)
        
        # Hiển thị kết quả dưới dạng bảng
        st.subheader(f'Kết quả phân tích {algorithm}:')
        st.dataframe(result_df)
        
        # Tạo đồ thị
        graph_image = plot_graph(G)
        st.subheader('Đồ thị liên kết:')
        st.image(f"data:image/png;base64,{graph_image}", use_column_width=True)

# Chạy ứng dụng Streamlit
if __name__ == '__main__':
    main()
