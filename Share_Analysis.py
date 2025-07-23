import pandas as pd
import streamlit as st
import yfinance

@st.cache_data
def load_data():
    components = pd.read_html('https://en.wikipedia.org/wiki/List_of_S'
                    '%26P_500_companies')[0]
    return components.set_index('Symbol')


@st.cache_data
def load_quotes(asset):
    return yfinance.download(asset, period="6mo", group_by='ticker')


def main():
    components = load_data()
    title = st.empty()
    st.sidebar.title("Options")

    def label(symbol):
        a = components.loc[symbol]
        return symbol + ' - ' + a.Security

    if st.sidebar.checkbox('View companies list'):
        st.dataframe(components[['Security',
                                 'GICS Sector',
                                 'Date first added',
                                 'Founded']])

    st.sidebar.subheader('Select a company')
    asset = st.sidebar.selectbox('Click below to select a new company',
                                 components.index.sort_values(), index=3,
                                 format_func=label)
    title.title(components.loc[asset].Security)
    if st.sidebar.checkbox('View company info', True):
        st.table(components.loc[asset])

    # Sanitize ticker for yfinance compatibility (e.g., 'BRK.B' -> 'BRK-B')
    ticker = asset.replace('.', '-')
    data0 = load_quotes(ticker)
    data = data0.copy().dropna()
    data.index.name = None

    if data.empty:
        st.error(f"Could not load data for '{asset}'. The ticker may be invalid, delisted, or there might be a network issue.")
        st.stop()

    # In some cases, yfinance returns a multi-index column, even for a single ticker.
    # We flatten it to a single index by dropping the 'ticker' level.
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(0)

    section = st.sidebar.slider('Number of quotes to display', min_value=30,
                        max_value=data.shape[0],
                        value=data.shape[0],  step=10)

    data2 = data[-section:][['Close']]

    sma = st.sidebar.checkbox('SMA')
    if sma:
        period = st.sidebar.slider('SMA period', min_value=5, max_value=500,
                             value=20,  step=1)
        data[f'SMA {period}'] = data['Close'].rolling(period ).mean()
        data2[f'SMA {period}'] = data[f'SMA {period}'].reindex(data2.index)

    sma2 = st.sidebar.checkbox('SMA2')
    if sma2:
        period2 = st.sidebar.slider('SMA2 period', min_value=5, max_value=500,
                             value=50,  step=1)
        data[f'SMA2 {period2}'] = data['Close'].rolling(period2).mean()
        data2[f'SMA2 {period2}'] = data[f'SMA2 {period2}'].reindex(data2.index)

    st.subheader('Chart')
    st.line_chart(data2)

    if st.sidebar.checkbox('View stadistic'):
        st.subheader('Stadistic')
        st.table(data2.describe())

    if st.sidebar.checkbox('View quotes'):
        st.subheader(f'{asset} historical data')
        st.write(data2)

    st.sidebar.title("About")
    st.sidebar.info('This app is a simple example of '
                    'using Strealit to create a financial data web app.\n'
                    '\nIt is maintained by [Roshan Leanage]('
                    'Check the code at https://github.com/Ross-123/Stock_Analysis/tree/main')

if __name__ == '__main__':
    main()
