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