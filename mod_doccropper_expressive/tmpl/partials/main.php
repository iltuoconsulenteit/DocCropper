<div class="flex flex-1 overflow-hidden">
  <div x-show="drawer" class="fixed inset-0 z-40 flex md:hidden">
    <div class="bg-white w-64 p-4" @click.away="drawer=false">
      <nav>
        <a href="#" class="block py-2" @click="tab='export'; drawer=false">Export</a>
        <a href="#" class="block py-2" @click="tab='files'; drawer=false">Files</a>
      </nav>
    </div>
    <div class="flex-1 bg-black opacity-50" @click="drawer=false"></div>
  </div>
  <aside class="hidden md:block md:w-64 bg-gray-100 p-4">
    <nav>
      <a href="#" class="block py-2" :class="{'font-bold':tab==='export'}" @click="tab='export'">Export</a>
      <a href="#" class="block py-2" :class="{'font-bold':tab==='files'}" @click="tab='files'">Files</a>
    </nav>
  </aside>
  <main class="flex-1 p-4 overflow-y-auto">
    <template x-if="tab==='export'">
      <div class="space-y-4">
        <button class="px-4 py-2 bg-blue-600 text-white rounded" @click="exporting=true; await window.DC.export(); exporting=false">Export PDF</button>
      </div>
    </template>
    <template x-if="tab==='files'">
      <div class="text-gray-500">Files tab content</div>
    </template>
  </main>
</div>
