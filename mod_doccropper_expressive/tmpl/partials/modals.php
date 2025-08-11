<div x-show="showModal" x-transition class="fixed inset-0 z-50 flex items-end md:items-center justify-center">
  <div class="absolute inset-0 bg-black opacity-50" @click="showModal=false"></div>
  <div class="bg-white w-full md:w-1/3 p-6 rounded-t-2xl md:rounded-xl relative">
    <h2 class="text-xl font-semibold mb-4">Export ready</h2>
    <div class="flex space-x-2">
      <button class="flex-1 px-4 py-2 bg-green-600 text-white rounded" @click="window.DC.download()">Download</button>
      <button class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded" @click="window.DC.sign()">Sign</button>
    </div>
    <button class="absolute top-2 right-2 text-gray-500" @click="showModal=false">&times;</button>
  </div>
</div>
