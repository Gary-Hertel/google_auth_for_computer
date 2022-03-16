# README

------



电脑桌面版谷歌身份验证器。



登录一些账号时每次都要输入谷歌验证码，每次都去拿手机还挺麻烦的，所以就整一个电脑桌面版啦。

效果如下：

![WX20220317-022028@2x](https://tva1.sinaimg.cn/large/e6c9d24ely1h0cacalig2j20k016oach.jpg)



## 使用方法：

+   安装依赖：`pip install -r requirements.txt` （如果提示没有模块，就缺啥装啥）
+   初次打开是空白的，需要导入，但是只能一个一个地导入，不支持批量导入。手机上的谷歌验证器可以导出，选中某一个后导出就会显示二维码，然后点击桌面版谷歌验证器上的**导入**按钮，会调用电脑摄像头，建议多点击几次，这样容易识别成功。然后停止后重新运行就可以看到了。
+   可以自己打包成mac或windows可执行程序。
