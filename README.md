# 打包

使用 PyInstaller（包含 assets、app/data 与 VLC 运行库）：

CMD：
```bat
pyinstaller --noconfirm --onedir --noconsole --name "MusicPlayer" ^
  --icon "assets/icons/application.ico" ^
  --add-data "assets;assets" ^
  --add-data "app/data;app/data" ^
  --add-data "third_party/vlc/plugins;plugins" ^
  --add-binary "third_party/vlc/libvlc.dll;." ^
  --add-binary "third_party/vlc/libvlccore.dll;." ^
  run.py
```

PowerShell：
```powershell
pyinstaller --noconfirm --onedir --noconsole --name "MusicPlayer" `
  --icon "assets/icons/application.ico" `
  --add-data "assets;assets" `
  --add-data "app/data;app/data" `
  --add-data "third_party/vlc/plugins;plugins" `
  --add-binary "third_party/vlc/libvlc.dll;." `
  --add-binary "third_party/vlc/libvlccore.dll;." `
  run.py
```

顺序
随机
循环
调节音量
歌词
暂停和播放一个按钮
空格暂停
键盘左右键控制切歌