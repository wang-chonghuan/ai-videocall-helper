const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 520,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  // 移除窗口菜单栏
  win.setMenu(null);

  // 检查是否有环境变量指示使用预览模式
  const isProd = process.env.NODE_ENV === 'production';
  const isPreview = process.env.USE_PREVIEW === 'true';
  
  if (isPreview) {
    // 预览服务器模式
    win.loadURL('http://localhost:4173');
  } else if (!isProd) {
    // 开发模式：加载Vite开发服务器
    win.loadURL('http://localhost:5173');
    // win.webContents.openDevTools(); // 注释掉自动打开DevTools
  } else {
    // 生产模式：直接加载构建后的文件
    win.loadFile(path.join(__dirname, '..', 'dist/index.html'));
  }
}

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
}); 