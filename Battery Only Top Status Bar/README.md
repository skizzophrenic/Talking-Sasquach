Since I was creating all these animations, I wanted a way to minimise the clutter on the top bar.  Since FiskerWhisker and E-Sure kindly already figured out how to remove the ribbon cable connecting the left and right status bars, I figured I'd go one step further and completely remove the left icon bar and remove the shadow on the battery bar.  I have 3 versions, normal battery bar, battery bar without the shadow, and what I have found to be the least battery bar you can get away with without it looking bad.

The gui.c files go into your applications\services\gui\ folder before compiling the firmware.  Then just compile and flash as normal!

Minimal

![Minimal](https://user-images.githubusercontent.com/16942638/195594733-e62f21b5-dde7-4c56-b179-32f8b4274c37.png)

Full Power Bar

![FullPower](https://user-images.githubusercontent.com/16942638/195594748-4678e8ac-8794-42ab-b40a-5dafbd27582d.png)

Power bar without the shadow

![Smaller Power Bar](https://user-images.githubusercontent.com/16942638/195594821-1e749024-b4bd-487e-bccf-5b5c1991eff8.png)

No Power Bar

![No Battery Icon](https://user-images.githubusercontent.com/16942638/195629013-bfd2f688-689b-4c11-bc6f-df158b7bf5f7.png)
