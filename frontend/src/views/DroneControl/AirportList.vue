<template>
  <aside class="airport-list">
    <div class="list-header">
      <div>
        <span class="section-kicker">AIRPORT LIST</span>
        <h3>机场列表</h3>
      </div>
      <el-button
        type="primary"
        link
        :loading="loading"
        @click="$emit('refresh')"
      >
        刷新
      </el-button>
    </div>

    <div class="airport-items">
      <button
        v-for="dock in docks"
        :key="dock.dockCode"
        type="button"
        class="airport-card"
        :class="{
          active: dock.droneCode === selectedDeviceCode,
          offline: dock.status !== 'online'
        }"
        @click="$emit('select', dock.droneCode)"
      >
        <div class="airport-title-row">
          <div class="airport-name">
            <span
              class="status-dot"
              :class="dock.status"
            />
            <strong>{{ dock.dockName }}</strong>
          </div>
          <span
            class="status-pill"
            :class="dock.status"
          >
            {{ dock.status === 'online' ? '在线' : '离线' }}
          </span>
        </div>

        <dl>
          <div>
            <dt>机场编号</dt>
            <dd>{{ dock.dockCode }}</dd>
          </div>
          <div>
            <dt>无人机</dt>
            <dd>{{ dock.droneCode || '--' }}</dd>
          </div>
          <div>
            <dt>位置状态</dt>
            <dd>{{ dock.droneInDock ? '机舱内' : '机舱外' }}</dd>
          </div>
        </dl>
      </button>
    </div>

    <el-empty
      v-if="!loading && docks.length === 0"
      description="暂无机场数据"
      :image-size="80"
    />

    <div class="location-panel">
      <span>最新位置</span>
      <strong>{{ selectedDock?.location || '暂无位置数据' }}</strong>
      <em v-if="selectedDock">
        {{ selectedDock.droneInDock ? '机舱内' : '机舱外' }}
      </em>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  docks: {
    type: Array,
    default: () => []
  },
  selectedDeviceCode: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['select', 'refresh'])

const selectedDock = computed(() => {
  return props.docks.find(
    dock => dock.droneCode === props.selectedDeviceCode
  )
})
</script>

<style scoped>
.airport-list {
  display: flex;
  flex-direction: column;
  min-height: 620px;
  padding: 20px;
  background: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.list-header,
.airport-title-row,
.airport-name,
.location-panel {
  display: flex;
  align-items: center;
}

.list-header,
.airport-title-row {
  justify-content: space-between;
}

.list-header {
  margin-bottom: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid #ebeef5;
}

.section-kicker {
  color: #409eff;
  font-size: 10px;
  letter-spacing: 1.8px;
}

.list-header h3 {
  margin: 3px 0 0;
  color: #303133;
  font-size: 22px;
}

.airport-items {
  display: grid;
  gap: 12px;
}

.airport-card {
  width: 100%;
  padding: 16px;
  color: #606266;
  text-align: left;
  background: #fafafa;
  border: 1px solid #dcdfe6;
  border-radius: 10px;
  cursor: pointer;
  transition: 0.2s ease;
}

.airport-card:hover,
.airport-card.active {
  background: #ecf5ff;
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.12);
  transform: translateY(-1px);
}

.airport-card.offline {
  opacity: 0.62;
}

.airport-name {
  gap: 8px;
  color: #303133;
  font-size: 16px;
}

.status-dot {
  width: 9px;
  height: 9px;
  background: #909399;
  border-radius: 50%;
}

.status-dot.online {
  background: #67c23a;
  box-shadow: 0 0 7px rgba(103, 194, 58, 0.55);
}

.status-pill {
  padding: 3px 10px;
  color: #f56c6c;
  font-size: 12px;
  background: #fef0f0;
  border: 1px solid #fab6b6;
  border-radius: 16px;
}

.status-pill.online {
  color: #67c23a;
  background: #f0f9eb;
  border-color: #b3e19d;
}

.airport-card dl {
  display: grid;
  gap: 7px;
  margin: 14px 0 0;
}

.airport-card dl div {
  display: grid;
  grid-template-columns: 76px 1fr;
}

.airport-card dt {
  color: #909399;
}

.airport-card dd {
  margin: 0;
  color: #606266;
  font-family: Consolas, monospace;
}

.location-panel {
  flex-wrap: wrap;
  gap: 8px 12px;
  margin-top: auto;
  padding-top: 18px;
  border-top: 1px solid #ebeef5;
}

.location-panel span {
  color: #909399;
}

.location-panel strong {
  color: #409eff;
}

.location-panel em {
  margin-left: auto;
  padding: 3px 9px;
  color: #606266;
  font-size: 12px;
  font-style: normal;
  background: #f2f6fc;
  border-radius: 14px;
}
</style>
