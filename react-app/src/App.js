import './App.css';

import {
  QueryClient,
  QueryClientProvider,
  useQuery,
} from '@tanstack/react-query'

const queryClient = new QueryClient()

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <QueryClientProvider client={queryClient}>
          <Example />
        </QueryClientProvider>
      </header>
    </div>
  );
}

function Example() {
  const { isPending, error, data } = useQuery({
    queryKey: ['repoData'],
    queryFn: () =>
      fetch('http://localhost:5000/daily_prediction').then((res) =>
        res.json(),
      ),
  })

  if (isPending) return 'Loading...'

  if (error) return 'An error has occurred: ' + error.message

  return (
    <div>
      <h1 className='Prediction-band'>Today, {data.day} the spot price of wheat will <strong>{data.prediction > 0 ? "GO UP" : "GO DOWN"}</strong></h1>
    </div>
  )
  }
export default App;
