import Chatbot from '@/components/Chatbot';
import logo from '@/assets/images/ComplyScan(3).svg';

function App() {

  return (
    <div className='flex flex-col min-h-full w-full max-w-3xl mx-auto px-4'>
      <header className='sticky top-0 shrink-0 z-20 bg-white'>
        <div className='flex flex-col h-full w-full gap-1 pt-4 pb-2'>
        <img src={logo} className='w-48' alt='logo' />
<h1 className='font-urbanist text-[1.65rem] font-semibold text-neutral-800'>
  <span className="text-red-600">AI Agent</span> for Web Accessibility & Compliance Check
</h1>

        </div>
      </header>
      <Chatbot />
    </div>
  );
}

export default App;