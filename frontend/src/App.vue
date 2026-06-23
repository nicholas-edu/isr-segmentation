<template>
  <div class="min-h-screen gradient-bg">
    <!-- Header -->
    <header class="bg-black bg-opacity-40 text-white py-6 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold">ISR</h1>
            <p class="text-sm text-gray-200 mt-1">Natural Language Satellite Image Segmentation</p>
          </div>
          <div v-if="modelStatus.loaded" class="text-right">
            <p class="text-xs text-green-300">✓ Model Ready</p>
            <p class="text-xs text-gray-300">{{ modelStatus.model }}</p>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Upload & Input Section -->
        <div class="space-y-6">
          <!-- Upload Area -->
          <div
            @click="$refs.fileInput.click()"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleDrop"
            :class="['glass-effect rounded-2xl p-8 border-2 border-dashed cursor-pointer transition-all', isDragging ? 'border-blue-400 bg-blue-50 bg-opacity-10' : 'border-white border-opacity-30']"
          >
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              @change="handleFileSelect"
              class="hidden"
            />
            <div class="text-center">
              <div class="text-4xl mb-3">📸</div>
              <h3 class="text-xl font-semibold text-gray-800 mb-1">Upload Satellite Image</h3>
              <p class="text-gray-600 text-sm">Drag and drop or click to select</p>
              <p class="text-gray-500 text-xs mt-2">PNG, JPG, TIFF up to 25MB</p>
            </div>
          </div>

          <!-- Image Preview -->
          <div v-if="originalImage" class="glass-effect rounded-xl overflow-hidden">
            <img :src="originalImage" alt="Original" class="w-full h-auto" />
            <div class="p-4 border-t border-gray-200">
              <p class="text-xs text-gray-600">
                Size: {{ imageSize.width }} × {{ imageSize.height }}px
              </p>
            </div>
          </div>

          <!-- Prompt Input -->
          <div class="glass-effect rounded-xl p-6">
            <label class="block text-sm font-semibold text-gray-800 mb-3">
              📝 What do you want to segment?
            </label>
            <div class="space-y-3">
              <textarea
                v-model="prompt"
                placeholder="e.g., 'buildings in urban areas', 'forest coverage', 'water bodies', 'road networks'"
                class="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 resize-none"
                rows="4"
              ></textarea>
              <p class="text-xs text-gray-500">Be specific for better results</p>
            </div>

            <!-- Suggested Prompts -->
            <div class="mt-4">
              <p class="text-xs font-semibold text-gray-700 mb-2">💡 Suggested prompts:</p>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="suggestion in suggestedPrompts"
                  :key="suggestion"
                  @click="prompt = suggestion"
                  class="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition"
                >
                  {{ suggestion }}
                </button>
              </div>
            </div>
          </div>

          <!-- Segment Button -->
          <button
            @click="segment"
            :disabled="!originalImage || !prompt || isProcessing"
            :class="['w-full py-3 px-6 rounded-lg font-semibold text-white transition-all duration-300', isProcessing || !originalImage || !prompt ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600 active:scale-95']"
          >
            <span v-if="!isProcessing" class="flex items-center justify-center gap-2">
              ✨ Segment Image
            </span>
            <span v-else class="flex items-center justify-center gap-2">
              <span class="loading-spinner"></span>
              Processing...
            </span>
          </button>
        </div>

        <!-- Results Section -->
        <div class="space-y-6">
          <!-- Segmentation Result -->
          <div v-if="segmentationResult" class="glass-effect rounded-xl overflow-hidden">
            <div class="bg-green-500 text-white p-4">
              <p class="font-semibold">✓ Segmentation Complete</p>
            </div>
            <div class="p-4">
              <p class="text-sm font-semibold text-gray-800 mb-3">Result:</p>
              <img
                v-if="segmentationResult.visualization_base64"
                :src="`data:image/png;base64,${segmentationResult.visualization_base64}`"
                alt="Segmentation Result"
                class="w-full rounded-lg mb-4"
              />
              <div class="bg-blue-50 p-3 rounded-lg">
                <p class="text-xs font-semibold text-gray-700 mb-1">Prompt used:</p>
                <p class="text-sm text-gray-600 italic">{{ segmentationResult.prompt }}</p>
              </div>
            </div>
          </div>

          <!-- No Results Yet -->
          <div v-else class="glass-effect rounded-xl p-12 text-center">
            <div class="text-6xl mb-4">🎯</div>
            <p class="text-gray-600">Upload an image and describe what you want to segment</p>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
            <p class="font-semibold">Error</p>
            <p class="text-sm">{{ error }}</p>
            <button @click="error = null" class="text-xs mt-2 underline">Dismiss</button>
          </div>

          <!-- Stats -->
          <div v-if="stats" class="glass-effect rounded-xl p-6">
            <h3 class="font-semibold text-gray-800 mb-4">📊 Statistics</h3>
            <div class="grid grid-cols-2 gap-4">
              <div class="bg-blue-50 p-3 rounded-lg">
                <p class="text-xs text-gray-600">Processing Time</p>
                <p class="text-lg font-bold text-blue-600">{{ stats.processingTime }}ms</p>
              </div>
              <div class="bg-green-50 p-3 rounded-lg">
                <p class="text-xs text-gray-600">Model</p>
                <p class="text-xs font-bold text-green-600 truncate">ISR</p>
              </div>
            </div>
          </div>

          <!-- Download Button -->
          <button
            v-if="segmentationResult"
            @click="downloadResult"
            class="w-full py-2 px-4 bg-green-500 hover:bg-green-600 text-white rounded-lg font-semibold transition"
          >
            ⬇️ Download Result
          </button>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-black bg-opacity-40 text-white text-center py-6 mt-12">
      <p class="text-sm">ISR Demo v1.0 | Powered by Qwen-2.5-VL + SAM2</p>
    </footer>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import axios from 'axios'

export default {
  name: 'App',
  setup() {
    const fileInput = ref(null)
    const originalImage = ref(null)
    const imageSize = ref({ width: 0, height: 0 })
    const prompt = ref('')
    const isProcessing = ref(false)
    const isDragging = ref(false)
    const segmentationResult = ref(null)
    const error = ref(null)
    const stats = ref(null)
    const modelStatus = ref({ loaded: true, model: 'Think2Seg-RS-7B' })

    const suggestedPrompts = [
      'buildings',
      'roads and highways',
      'vegetation and forests',
      'water bodies',
      'urban development',
      'agricultural land'
    ]

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        loadImage(file)
      }
    }

    const handleDrop = (event) => {
      isDragging.value = false
      const files = event.dataTransfer.files
      if (files.length > 0 && files[0].type.startsWith('image/')) {
        loadImage(files[0])
      }
    }

    const loadImage = (file) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        originalImage.value = e.target.result
        const img = new Image()
        img.onload = () => {
          imageSize.value = { width: img.width, height: img.height }
        }
        img.src = e.target.result
      }
      reader.readAsDataURL(file)
    }

    const segment = async () => {
      if (!originalImage.value || !prompt.value) return

      isProcessing.value = true
      error.value = null
      segmentationResult.value = null
      stats.value = null

      try {
        const startTime = Date.now()

        // Convert base64 to file
        const base64Data = originalImage.value.split(',')[1]
        const byteCharacters = atob(base64Data)
        const byteNumbers = new Array(byteCharacters.length)
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i)
        }
        const byteArray = new Uint8Array(byteNumbers)
        const blob = new Blob([byteArray], { type: 'image/png' })

        // Create form data
        const formData = new FormData()
        formData.append('file', blob, 'image.png')
        formData.append('prompt', prompt.value)

        // Send to API
        const response = await axios.post('/api/segment', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        if (response.data.success) {
          segmentationResult.value = response.data
          stats.value = {
            processingTime: Date.now() - startTime
          }
        } else {
          error.value = response.data.error || 'Segmentation failed'
        }
      } catch (err) {
        console.error('Segmentation error:', err)
        error.value = err.response?.data?.detail || err.message || 'An error occurred during segmentation'
      } finally {
        isProcessing.value = false
      }
    }

    const downloadResult = () => {
      if (!segmentationResult.value?.visualization_base64) return

      const link = document.createElement('a')
      link.href = `data:image/png;base64,${segmentationResult.value.visualization_base64}`
      link.download = `isr-result-${Date.now()}.png`
      link.click()
    }

    return {
      fileInput,
      originalImage,
      imageSize,
      prompt,
      isProcessing,
      isDragging,
      segmentationResult,
      error,
      stats,
      modelStatus,
      suggestedPrompts,
      handleFileSelect,
      handleDrop,
      segment,
      downloadResult
    }
  }
}
</script>
