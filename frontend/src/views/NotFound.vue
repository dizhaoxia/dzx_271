<template>
  <Layout>
    <div class="page-container">
      <el-result icon="warning" title="404" sub-title="页面不存在">
        <template #extra>
          <el-button type="primary" @click="$router.replace('/home')">返回首页</el-button>
        </template>
      </el-result>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import Layout from '@/components/Layout.vue'
</script>
