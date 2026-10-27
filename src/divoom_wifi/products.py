"""Explicit product APIs generated from reviewed metadata; see tools/build_reference.py."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .client import BaseDevice


class Pixoo64(BaseDevice):
    """Pixoo64 operations from the official WiFi reference."""
    product_name = "pixoo64"

    def reboot(self) -> dict[str, Any]:
        """System reboots.

        Sources: https://docin.divoom-gz.com/web/#/5/26
        """
        return self.call("reboot")

    def get_dial_types(self) -> dict[str, Any]:
        """Dial Type.

        Sources: https://docin.divoom-gz.com/web/#/5/27
        """
        return self.call("get_dial_types")

    def get_dial_list(self, *, dial_type: str, page: int | None = None) -> dict[str, Any]:
        """Dial List.

        :param dial_type: dial type (wire: DialType)

        :param page: the number of pages,for example: 1, Notes: 30 per page (wire: Page)

        Sources: https://docin.divoom-gz.com/web/#/5/28
        """
        return self.call("get_dial_list", dial_type=dial_type, page=page)

    def select_clock(self, *, clock_id: int) -> dict[str, Any]:
        """Select faces Channel.

        :param clock_id: face id (wire: ClockId)

        Sources: https://docin.divoom-gz.com/web/#/5/29
        """
        return self.call("select_clock", clock_id=clock_id)

    def get_current_clock(self) -> dict[str, Any]:
        """Get select face id.

        Sources: https://docin.divoom-gz.com/web/#/5/30
        """
        return self.call("get_current_clock")

    def select_channel(self, *, select_index: int) -> dict[str, Any]:
        """select channel.

        :param select_index: channel id 0~3 ；0:Faces;1:Cloud Channdle;2:Visualizer;3:Custom;4:black screen (wire: SelectIndex)

        Sources: https://docin.divoom-gz.com/web/#/5/31
        """
        return self.call("select_channel", select_index=select_index)

    def select_custom_page(self, *, custom_page_index: int) -> dict[str, Any]:
        """control custom channel.

        :param custom_page_index: custom index  0~２ (wire: CustomPageIndex)

        Sources: https://docin.divoom-gz.com/web/#/5/32
        """
        return self.call("select_custom_page", custom_page_index=custom_page_index)

    def select_visualizer(self, *, eq_position: int) -> dict[str, Any]:
        """Visualizer Channel.

        :param eq_position: index :start from 0 (wire: EqPosition)

        Sources: https://docin.divoom-gz.com/web/#/5/33
        """
        return self.call("select_visualizer", eq_position=eq_position)

    def select_cloud_channel(self, *, index: int) -> dict[str, Any]:
        """Cloud Channel.

        :param index: cloud index 0~2; 0:Recommend gallery;1:Favourite;2:Subscribe artist;3:album (wire: Index)

        Sources: https://docin.divoom-gz.com/web/#/5/34
        """
        return self.call("select_cloud_channel", index=index)

    def get_current_channel(self) -> dict[str, Any]:
        """get cureent channel.

        Sources: https://docin.divoom-gz.com/web/#/5/35
        """
        return self.call("get_current_channel")

    def set_brightness(self, *, brightness: int) -> dict[str, Any]:
        """set brightness.

        :param brightness: 0~100 (wire: Brightness)

        Sources: https://docin.divoom-gz.com/web/#/5/36
        """
        return self.call("set_brightness", brightness=brightness)

    def get_settings(self) -> dict[str, Any]:
        """get all setting.

        Sources: https://docin.divoom-gz.com/web/#/5/37
        """
        return self.call("get_settings")

    def set_weather_location(self, *, longitude: str, latitude: str) -> dict[str, Any]:
        """Weather area setting.

        :param longitude: value (wire: Longitude)

        :param latitude: value (wire: Latitude)

        Sources: https://docin.divoom-gz.com/web/#/5/38
        """
        return self.call("set_weather_location", longitude=longitude, latitude=latitude)

    def set_timezone(self, *, time_zone_value: str) -> dict[str, Any]:
        """Set Time Zone .

        :param time_zone_value: time zone value (wire: TimeZoneValue)

        Sources: https://docin.divoom-gz.com/web/#/5/39
        """
        return self.call("set_timezone", time_zone_value=time_zone_value)

    def set_utc(self, *, utc: int) -> dict[str, Any]:
        """system Time.

        :param utc: utc time (wire: Utc)

        Sources: https://docin.divoom-gz.com/web/#/5/40
        """
        return self.call("set_utc", utc=utc)

    def set_screen(self, *, on_off: int) -> dict[str, Any]:
        """Screen switch.

        :param on_off: 1:on; 0:off (wire: OnOff)

        Sources: https://docin.divoom-gz.com/web/#/5/41
        """
        return self.call("set_screen", on_off=on_off)

    def get_device_time(self) -> dict[str, Any]:
        """Get Device Time.

        Sources: https://docin.divoom-gz.com/web/#/5/42
        """
        return self.call("get_device_time")

    def set_temperature_mode(self, *, mode: int) -> dict[str, Any]:
        """Set temperature mode.

        :param mode: 0:Celsius;1:Fahrenheit (wire: Mode)

        Sources: https://docin.divoom-gz.com/web/#/5/43
        """
        return self.call("set_temperature_mode", mode=mode)

    def set_rotation(self, *, mode: int) -> dict[str, Any]:
        """Set  Rotation angle.

        :param mode: 0:normal,1:90;2:180;3:270 (wire: Mode)

        Sources: https://docin.divoom-gz.com/web/#/5/44
        """
        return self.call("set_rotation", mode=mode)

    def set_mirror_mode(self, *, mode: int) -> dict[str, Any]:
        """Set  Mirror mode.

        :param mode: 0:disable;1:enalbe (wire: Mode)

        Sources: https://docin.divoom-gz.com/web/#/5/45
        """
        return self.call("set_mirror_mode", mode=mode)

    def set_hour_mode(self, *, mode: int) -> dict[str, Any]:
        """Set  hour mode.

        :param mode: 1:24－hour;0:12-hour (wire: Mode)

        Sources: https://docin.divoom-gz.com/web/#/5/46
        """
        return self.call("set_hour_mode", mode=mode)

    def set_highlight_mode(self, *, mode: int) -> dict[str, Any]:
        """Set  High Ligit mode.

        :param mode: 0:close;1:open (wire: Mode)

        Sources: https://docin.divoom-gz.com/web/#/5/47
        """
        return self.call("set_highlight_mode", mode=mode)

    def set_white_balance(self, *, r_value: int, g_value: int, b_value: int) -> dict[str, Any]:
        """Set  White Balance.

        :param r_value: 100 ;(0~100) (wire: RValue)

        :param g_value: 100 ;(0~100) (wire: GValue)

        :param b_value: 100 ;(0~100) (wire: BValue)

        Sources: https://docin.divoom-gz.com/web/#/5/48
        """
        return self.call("set_white_balance", r_value=r_value, g_value=g_value, b_value=b_value)

    def get_weather(self) -> dict[str, Any]:
        """Get the Weather  of the device.

        Sources: https://docin.divoom-gz.com/web/#/5/49
        """
        return self.call("get_weather")

    def set_gallery_time(self, *, single_galley_time: int, gallery_show_time_flag: int | None = None) -> dict[str, Any]:
        """SetGalleryTime.

        :param single_galley_time: the play time (wire: SingleGalleyTime)

        :param gallery_show_time_flag: 1: display time; 0:none (wire: GalleryShowTimeFlag)

        Sources: https://docin.divoom-gz.com/web/#/5/137, https://docin.divoom-gz.com/web/#/5/355
        """
        return self.call("set_gallery_time", single_galley_time=single_galley_time, gallery_show_time_flag=gallery_show_time_flag)

    def set_countdown(self, *, minute: int, second: int, status: int) -> dict[str, Any]:
        """Set countdown tool.

        :param minute: the countdown's minute (wire: Minute)

        :param second: the countdown's second (wire: Second)

        :param status: 1: start; 0: stop (wire: Status)

        Sources: https://docin.divoom-gz.com/web/#/5/50
        """
        return self.call("set_countdown", minute=minute, second=second, status=status)

    def set_stopwatch(self, *, status: int) -> dict[str, Any]:
        """Set stopwatch tool.

        :param status: 2:reset;1: start; 0: stop (wire: Status)

        Sources: https://docin.divoom-gz.com/web/#/5/51
        """
        return self.call("set_stopwatch", status=status)

    def set_scoreboard(self, *, blue_score: int, red_score: int) -> dict[str, Any]:
        """Set scoreboard tool.

        :param blue_score: the blue score 0~999 (wire: BlueScore)

        :param red_score: the red score 0~999 (wire: RedScore)

        Sources: https://docin.divoom-gz.com/web/#/5/52
        """
        return self.call("set_scoreboard", blue_score=blue_score, red_score=red_score)

    def set_noise_tool(self, *, noise_status: int) -> dict[str, Any]:
        """Set noise tool.

        :param noise_status: 1:start; 0:stop (wire: NoiseStatus)

        Sources: https://docin.divoom-gz.com/web/#/5/53
        """
        return self.call("set_noise_tool", noise_status=noise_status)

    def play_gif(self, *, file_type: int, file_name: str) -> dict[str, Any]:
        """play gif.

        :param file_type: 2:play net file;  other is err (wire: FileType)

        :param file_name: 2:net file address; (wire: FileName)

        Sources: https://docin.divoom-gz.com/web/#/5/54
        """
        return self.call("play_gif", file_type=file_type, file_name=file_name)

    def get_animation_id(self) -> dict[str, Any]:
        """Get  sending animation PicId .

        Sources: https://docin.divoom-gz.com/web/#/5/55
        """
        return self.call("get_animation_id")

    def reset_animation_id(self) -> dict[str, Any]:
        """Reset  sending animation PicId.

        Sources: https://docin.divoom-gz.com/web/#/5/56
        """
        return self.call("reset_animation_id")

    def send_animation(self, *, pic_num: int, pic_width: int, pic_offset: int, pic_id: int, pic_speed: int, pic_data: str) -> dict[str, Any]:
        """Send animation.

        :param pic_num: the include single pictures of the animation and smaller than 60 (wire: PicNum)

        :param pic_width: the pixels of the animation, and only support the 16,32,64 (wire: PicWidth)

        :param pic_offset: the picture offset start from 0. eg:0,1,2,3,4,PicNum-1 (wire: PicOffset)

        :param pic_id: the animation ID, every animation must have unique ID and auto increase,It's getting bigger and start with 1, example: the current gif id is 100, and then next gif's id should be greater than or equal to 101 (wire: PicID)

        :param pic_speed: the animation speed, it bases on ms (wire: PicSpeed)

        :param pic_data: the picutre Base64 encoded RGB data, The RGB data is  left to right and up to down (wire: PicData)

        Sources: https://docin.divoom-gz.com/web/#/5/57
        """
        return self.call("send_animation", pic_num=pic_num, pic_width=pic_width, pic_offset=pic_offset, pic_id=pic_id, pic_speed=pic_speed, pic_data=pic_data)

    def send_text(self, *, text_id: int, x: int, y: int, dir: int, font: int, text_width: int, text_string: str, speed: int, color: str, align: int | None = None) -> dict[str, Any]:
        """Send Text.

        :param text_id: the text id is is unique and will be replaced with the same ID， it is samller than 20 (wire: TextId)

        :param x: the start x postion (wire: x)

        :param y: the start y postion (wire: y)

        :param dir: 0:scroll left, 1:scroll right (wire: dir)

        :param font: 0~7, app animation's font (wire: font)

        :param text_width: the text width is based point and bigger than 16, smaller than 64 (wire: TextWidth)

        :param text_string: the text string is utf8 string and lenght is smaller than 512 (wire: TextString)

        :param speed: the scroll speed if it need scroll, the time (ms) the text move one step (wire: speed)

        :param color: the font color, eg:#FFFF00 (wire: color)

        :param align: horizontal text alignment, 1:left; 2: middle; 3:right , it will support at 90102 version (wire: align)

        Sources: https://docin.divoom-gz.com/web/#/5/58
        """
        return self.call("send_text", text_id=text_id, x=x, y=y, dir=dir, font=font, text_width=text_width, text_string=text_string, speed=speed, color=color, align=align)

    def clear_text(self) -> dict[str, Any]:
        """Clear all text area.

        Sources: https://docin.divoom-gz.com/web/#/5/59
        """
        return self.call("clear_text")

    def get_fonts(self) -> dict[str, Any]:
        """Get font list.

        Sources: https://docin.divoom-gz.com/web/#/5/60
        """
        return self.call("get_fonts")

    def send_display_list(self, *, item_list: list[Any]) -> dict[str, Any]:
        """Send display list .

        :param item_list: item list (wire: ItemList)

        Sources: https://docin.divoom-gz.com/web/#/5/61
        """
        return self.call("send_display_list", item_list=item_list)

    def play_buzzer(self, *, active_time_in_cycle: int, off_time_in_cycle: int, play_total_time: int) -> dict[str, Any]:
        """Play Buzzer.

        :param active_time_in_cycle: Working time of buzzer in one cycle  in milliseconds (wire: ActiveTimeInCycle)

        :param off_time_in_cycle: Idle time of buzzer in one cycle in milliseconds (wire: OffTimeInCycle)

        :param play_total_time: Working total time of buzzer in milliseconds (wire: PlayTotalTime)

        Sources: https://docin.divoom-gz.com/web/#/5/62
        """
        return self.call("play_buzzer", active_time_in_cycle=active_time_in_cycle, off_time_in_cycle=off_time_in_cycle, play_total_time=play_total_time)

    def play_divoom_gif(self, *, file_id: str) -> dict[str, Any]:
        """play divoom gif.

        :param file_id: it is FileId (wire: FileId)

        Sources: https://docin.divoom-gz.com/web/#/5/63
        """
        return self.call("play_divoom_gif", file_id=file_id)

    def get_uploaded_images(self, *, device_id: int | None = None, device_mac: str | None = None, page: int | None = None) -> dict[str, Any]:
        """Get Img Upload List.

        :param device_id: Device ID (wire: DeviceId)

        :param device_mac: Device Mac, it can get from "Find device" (wire: DeviceMac)

        :param page: paged, default:1 (wire: Page)

        Sources: https://docin.divoom-gz.com/web/#/5/64
        """
        return self.call("get_uploaded_images", device_id=device_id, device_mac=device_mac, page=page)

    def get_liked_images(self, *, device_id: int | None = None, device_mac: str | None = None, page: int | None = None) -> dict[str, Any]:
        """Get My Like Img List.

        :param device_id: Device ID (wire: DeviceId)

        :param device_mac: Device Mac , it can get from "Find device" (wire: DeviceMac)

        :param page: paged, default:1 (wire: Page)

        Sources: https://docin.divoom-gz.com/web/#/5/65
        """
        return self.call("get_liked_images", device_id=device_id, device_mac=device_mac, page=page)

    def save_gif(self, *, local_name: str, net_name: str) -> dict[str, Any]:
        """save gif.

        :param local_name: local path (wire: LocalName)

        :param net_name: net file address; (wire: NetName)

        Sources: https://docin.divoom-gz.com/web/#/5/356
        """
        return self.call("save_gif", local_name=local_name, net_name=net_name)

    def play_gif_frame(self, *, file_name: str, frame_id: int) -> dict[str, Any]:
        """Play a frame of a GIF file.

        :param file_name: local path (wire: FileName)

        :param frame_id: the frame id; (wire: FrameId)

        Sources: https://docin.divoom-gz.com/web/#/5/357
        """
        return self.call("play_gif_frame", file_name=file_name, frame_id=frame_id)

    def send_command_list(self, *, command_list: list[Any]) -> dict[str, Any]:
        """Command list.

        :param command_list: the command array information (wire: CommandList)

        Sources: https://docin.divoom-gz.com/web/#/5/66
        """
        return self.call("send_command_list", command_list=command_list)

    def use_command_url(self, *, command_url: str) -> dict[str, Any]:
        """Url Command file.

        :param command_url: the url address of the command array information (wire: CommandUrl)

        Sources: https://docin.divoom-gz.com/web/#/5/67
        """
        return self.call("use_command_url", command_url=command_url)

class TimeGate(BaseDevice):
    """TimeGate operations from the official WiFi reference."""
    product_name = "timegate"

    def reboot(self) -> dict[str, Any]:
        """System reboots.

        Sources: https://docin.divoom-gz.com/web/#/5/140
        """
        return self.call("reboot")

    def set_brightness(self, *, brightness: int) -> dict[str, Any]:
        """set brightness.

        :param brightness: 0~100 (wire: Brightness)

        Sources: https://docin.divoom-gz.com/web/#/5/102
        """
        return self.call("set_brightness", brightness=brightness)

    def get_settings(self) -> dict[str, Any]:
        """get all setting.

        Sources: https://docin.divoom-gz.com/web/#/5/103
        """
        return self.call("get_settings")

    def set_weather_location(self, *, longitude: str, latitude: str) -> dict[str, Any]:
        """Weather area setting.

        :param longitude: value (wire: Longitude)

        :param latitude: value (wire: Latitude)

        Sources: https://docin.divoom-gz.com/web/#/5/104
        """
        return self.call("set_weather_location", longitude=longitude, latitude=latitude)

    def set_timezone(self, *, time_zone_value: str) -> dict[str, Any]:
        """Set Time Zone .

        :param time_zone_value: time zone value (wire: TimeZoneValue)

        Sources: https://docin.divoom-gz.com/web/#/5/105
        """
        return self.call("set_timezone", time_zone_value=time_zone_value)

    def set_utc(self, *, utc: int) -> dict[str, Any]:
        """system Time.

        :param utc: utc time (wire: Utc)

        Sources: https://docin.divoom-gz.com/web/#/5/106
        """
        return self.call("set_utc", utc=utc)

    def set_screen(self, *, on_off: int) -> dict[str, Any]:
        """Screen switch.

        :param on_off: 1:on; 0:off (wire: OnOff)

        Sources: https://docin.divoom-gz.com/web/#/5/107
        """
        return self.call("set_screen", on_off=on_off)

    def get_device_time(self) -> dict[str, Any]:
        """Get Device Time.

        Sources: https://docin.divoom-gz.com/web/#/5/108
        """
        return self.call("get_device_time")

    def set_temperature_mode(self, *, mode: int) -> dict[str, Any]:
        """Set temperature mode.

        :param mode: 0:Celsius;1:Fahrenheit (wire: Mode)

        Sources: https://docin.divoom-gz.com/web/#/5/109
        """
        return self.call("set_temperature_mode", mode=mode)

    def set_mirror_mode(self, *, mode: int) -> dict[str, Any]:
        """Set  Mirror mode.

        :param mode: 0:disable;1:enalbe (wire: Mode)

        Sources: https://docin.divoom-gz.com/web/#/5/110
        """
        return self.call("set_mirror_mode", mode=mode)

    def set_hour_mode(self, *, mode: int) -> dict[str, Any]:
        """Set  hour mode.

        :param mode: 1:24－hour;0:12-hour (wire: Mode)

        Sources: https://docin.divoom-gz.com/web/#/5/111
        """
        return self.call("set_hour_mode", mode=mode)

    def get_weather(self) -> dict[str, Any]:
        """Get the Weather  of the device.

        Sources: https://docin.divoom-gz.com/web/#/5/112
        """
        return self.call("get_weather")

    def set_gallery_time(self, *, single_galley_time: int, lcd_independence: int, lcd_index: int) -> dict[str, Any]:
        """SetGalleryTime.

        :param single_galley_time: the play time (wire: SingleGalleyTime)

        :param lcd_independence: the indepence id comes from IndependenceId in “Device/GetChannelInfo”, it is active if ChannelType is 1 (wire: LcdIndependence)

        :param lcd_index: 0~4  the lcd index (wire: LcdIndex)

        Sources: https://docin.divoom-gz.com/web/#/5/138
        """
        return self.call("set_gallery_time", single_galley_time=single_galley_time, lcd_independence=lcd_independence, lcd_index=lcd_index)

    def set_rgb(self, *, on_off: int | None = None, brightness: int | None = None, color: str | None = None, key_on_off: int | None = None, color_cycle: int | None = None, select_light_index: int | None = None, light_list: list[Any] | None = None) -> dict[str, Any]:
        """Set RGB Information.

        :param on_off: 0:on;1:off (wire: OnOff)

        :param brightness: 0~100 (wire: Brightness)

        :param color: #FF1F3D (wire: Color)

        :param key_on_off: 0:on;1:off , the keyboard light switch (wire: KeyOnOff)

        :param color_cycle: 0:on;1:off , the keyboard light switch (wire: ColorCycle)

        :param select_light_index: 0: all; 1:the edge rgb; 2:Backlight (wire: SelectLightIndex)

        :param light_list: setting (wire: LightList)

        Sources: https://docin.divoom-gz.com/web/#/5/353
        """
        return self.call("set_rgb", on_off=on_off, brightness=brightness, color=color, key_on_off=key_on_off, color_cycle=color_cycle, select_light_index=select_light_index, light_list=light_list)

    def get_dial_types(self) -> dict[str, Any]:
        """Sub Dial Type.

        Sources: https://docin.divoom-gz.com/web/#/5/113
        """
        return self.call("get_dial_types")

    def get_dial_list(self, *, dial_type: str, device_type: str | None = None, page: int | None = None) -> dict[str, Any]:
        """Indeividual Dial List.

        :param dial_type: dial type (wire: DialType)

        :param device_type: "LCD" (wire: DeviceType)

        :param page: the number of pages,for example: 1, Notes: 30 per page (wire: Page)

        Sources: https://docin.divoom-gz.com/web/#/5/114
        """
        return self.call("get_dial_list", dial_type=dial_type, device_type=device_type, page=page)

    def get_whole_dial_list(self, *, page: int | None = None) -> dict[str, Any]:
        """get whole dial List.

        :param page: the number of pages,for example: 1, Notes: 30 per page (wire: Page)

        Sources: https://docin.divoom-gz.com/web/#/5/115
        """
        return self.call("get_whole_dial_list", page=page)

    def select_whole_clock(self, *, clock_id: int) -> dict[str, Any]:
        """Select  Whole Dial.

        :param clock_id: face id, it comes from "whole Dial List" (wire: ClockId)

        Sources: https://docin.divoom-gz.com/web/#/5/116
        """
        return self.call("select_whole_clock", clock_id=clock_id)

    def select_channel_type(self, *, channel_type: int, lcd_independence: int | None = None) -> dict[str, Any]:
        """Select  Channel Type.

        :param channel_type: 0: the whole dial; 1: indenpence dial (wire: ChannelType)

        :param lcd_independence: the indepence id comes from IndependenceId in "Device/GetChannelInfo", it is active if ChannelType is 1 (wire: LcdIndependence)

        Sources: https://docin.divoom-gz.com/web/#/5/117
        """
        return self.call("select_channel_type", channel_type=channel_type, lcd_independence=lcd_independence)

    def get_channel_info(self, *, device_id: int | None = None, device_type: str | None = None) -> dict[str, Any]:
        """Get  Channel Information.

        :param device_id: the device id (wire: DeviceId)

        :param device_type: "LCD" (wire: DeviceType)

        Sources: https://docin.divoom-gz.com/web/#/5/118
        """
        return self.call("get_channel_info", device_id=device_id, device_type=device_type)

    def select_clock(self, *, clock_id: int, lcd_index: int, lcd_independence: int) -> dict[str, Any]:
        """Select Indeividual dial.

        :param clock_id: face id , it comes from "Sub Dial List" (wire: ClockId)

        :param lcd_index: the lcd id 0~4 (wire: LcdIndex)

        :param lcd_independence: independence dial id  comes from the LcdIndependence of "Get Channel Information" (wire: LcdIndependence)

        Sources: https://docin.divoom-gz.com/web/#/5/119
        """
        return self.call("select_clock", clock_id=clock_id, lcd_index=lcd_index, lcd_independence=lcd_independence)

    def select_visualizer(self, *, eq_position: int, lcd_index: int, lcd_independence: int) -> dict[str, Any]:
        """Select Indeividual Visualizer Channel.

        :param eq_position: index :start from 0 (wire: EqPosition)

        :param lcd_index: the lcd id 0~4 (wire: LcdIndex)

        :param lcd_independence: independence dial id (wire: LcdIndependence)

        Sources: https://docin.divoom-gz.com/web/#/5/120
        """
        return self.call("select_visualizer", eq_position=eq_position, lcd_index=lcd_index, lcd_independence=lcd_independence)

    def set_countdown(self, *, minute: int, second: int, status: int) -> dict[str, Any]:
        """Set countdown tool.

        :param minute: the countdown's minute (wire: Minute)

        :param second: the countdown's second (wire: Second)

        :param status: 1: start; 0: stop (wire: Status)

        Sources: https://docin.divoom-gz.com/web/#/5/121
        """
        return self.call("set_countdown", minute=minute, second=second, status=status)

    def set_stopwatch(self, *, status: int) -> dict[str, Any]:
        """Set stopwatch tool.

        :param status: 2:reset;1: start; 0: stop (wire: Status)

        Sources: https://docin.divoom-gz.com/web/#/5/122
        """
        return self.call("set_stopwatch", status=status)

    def set_scoreboard(self, *, blue_score: int, red_score: int) -> dict[str, Any]:
        """Set scoreboard tool.

        :param blue_score: the blue score 0~999 (wire: BlueScore)

        :param red_score: the red score 0~999 (wire: RedScore)

        Sources: https://docin.divoom-gz.com/web/#/5/123
        """
        return self.call("set_scoreboard", blue_score=blue_score, red_score=red_score)

    def set_noise_tool(self, *, noise_status: int) -> dict[str, Any]:
        """Set noise tool.

        :param noise_status: 1:start; 0:stop (wire: NoiseStatus)

        Sources: https://docin.divoom-gz.com/web/#/5/124
        """
        return self.call("set_noise_tool", noise_status=noise_status)

    def play_buzzer(self, *, active_time_in_cycle: int, off_time_in_cycle: int, play_total_time: int) -> dict[str, Any]:
        """Play Buzzer.

        :param active_time_in_cycle: Working time of buzzer in one cycle  in milliseconds (wire: ActiveTimeInCycle)

        :param off_time_in_cycle: Idle time of buzzer in one cycle in milliseconds (wire: OffTimeInCycle)

        :param play_total_time: Working total time of buzzer in milliseconds (wire: PlayTotalTime)

        Sources: https://docin.divoom-gz.com/web/#/5/125
        """
        return self.call("play_buzzer", active_time_in_cycle=active_time_in_cycle, off_time_in_cycle=off_time_in_cycle, play_total_time=play_total_time)

    def get_liked_images(self, *, device_id: int | None = None, device_mac: str | None = None, page: int | None = None) -> dict[str, Any]:
        """Get My Like Img List.

        :param device_id: Device ID (wire: DeviceId)

        :param device_mac: Device Mac , it can get from "Find device" (wire: DeviceMac)

        :param page: paged, default:1 (wire: Page)

        Sources: https://docin.divoom-gz.com/web/#/5/126
        """
        return self.call("get_liked_images", device_id=device_id, device_mac=device_mac, page=page)

    def get_uploaded_images(self, *, device_id: int | None = None, device_mac: str | None = None, page: int | None = None) -> dict[str, Any]:
        """Get Img Upload List.

        :param device_id: Device ID (wire: DeviceId)

        :param device_mac: Device Mac, it can get from "Find device" (wire: DeviceMac)

        :param page: paged, default:1 (wire: Page)

        Sources: https://docin.divoom-gz.com/web/#/5/127
        """
        return self.call("get_uploaded_images", device_id=device_id, device_mac=device_mac, page=page)

    def play_divoom_gif(self, *, file_id: str, lcd_array: list[Any]) -> dict[str, Any]:
        """play divoom gif.

        :param file_id: it is FileId (wire: FileId)

        :param lcd_array: [1,0,0,0,0] 1:display;0:pass (wire: LcdArray)

        Sources: https://docin.divoom-gz.com/web/#/5/128
        """
        return self.call("play_divoom_gif", file_id=file_id, lcd_array=lcd_array)

    def play_gif(self, *, lcd_array: list[Any], file_name: list[Any]) -> dict[str, Any]:
        """play gif.

        :param lcd_array: [1,0,0,0,0] 1:display;0:pass (wire: LcdArray)

        :param file_name: net file address, it is less than 10 files (wire: FileName)

        Sources: https://docin.divoom-gz.com/web/#/5/129
        """
        return self.call("play_gif", lcd_array=lcd_array, file_name=file_name)

    def play_gif_on_all_screens(self, *, lcd0_gif_file: list[Any], lcd1_gif_file: list[Any], lcd2_gif_file: list[Any], lcd3_gif_file: list[Any], lcd4_gif_file: list[Any]) -> dict[str, Any]:
        """play gif in all gif.

        :param lcd0_gif_file: LCD0 play gif files (wire: LCD0GifFile)

        :param lcd1_gif_file: LCD1 play gif files (wire: LCD1GifFile)

        :param lcd2_gif_file: LCD2 play gif files (wire: LCD2GifFile)

        :param lcd3_gif_file: LCD3 play gif files (wire: LCD3GifFile)

        :param lcd4_gif_file: LCD4 play gif files (wire: LCD4GifFile)

        Sources: https://docin.divoom-gz.com/web/#/5/130
        """
        return self.call("play_gif_on_all_screens", lcd0_gif_file=lcd0_gif_file, lcd1_gif_file=lcd1_gif_file, lcd2_gif_file=lcd2_gif_file, lcd3_gif_file=lcd3_gif_file, lcd4_gif_file=lcd4_gif_file)

    def send_animation(self, *, lcd_array: list[Any], pic_num: int, pic_width: int, pic_offset: int, pic_id: int, pic_speed: int, pic_data: str) -> dict[str, Any]:
        """Send animation.

        :param lcd_array: [1,0,0,0,0] 1:display;0:pass， it must be same in all frames (wire: LcdArray)

        :param pic_num: the include single pictures of the animation and smaller than 60 (wire: PicNum)

        :param pic_width: the pixels of the animation, and only support the 16,32,64,128 (wire: PicWidth)

        :param pic_offset: the picture offset start from 0. eg:0,1,2,3,4,PicNum-1 (wire: PicOffset)

        :param pic_id: the animation ID, every animation must have unique ID and auto increase,It's getting bigger and start with 1, example: the current gif id is 100, and then next gif's id should be greater than or equal to 101 (wire: PicID)

        :param pic_speed: the animation speed, it bases on ms (wire: PicSpeed)

        :param pic_data: the picutre Base64 encoded JPG data(https://www.rapidtables.com/web/tools/base64-encode.html), The JPEG data is  all binary data of the jpg file (wire: PicData)

        Sources: https://docin.divoom-gz.com/web/#/5/133
        """
        return self.call("send_animation", lcd_array=lcd_array, pic_num=pic_num, pic_width=pic_width, pic_offset=pic_offset, pic_id=pic_id, pic_speed=pic_speed, pic_data=pic_data)

    def send_text(self, *, lcd_index: int, text_id: int, x: int, y: int, dir: int, font: int, text_width: int, text_string: str, speed: int, color: str, align: int | None = None) -> dict[str, Any]:
        """Send Text.

        :param lcd_index: 0~4  it must be the first lcd index in Draw/SendHttpGif (wire: LcdIndex)

        :param text_id: the text id is is unique and will be replaced with the same ID， it is samller than 20 (wire: TextId)

        :param x: the start x postion (wire: x)

        :param y: the start y postion (wire: y)

        :param dir: 0:scroll left, 1:scroll right (wire: dir)

        :param font: 0~7, app animation's font (wire: font)

        :param text_width: the text width is based point and bigger than 16, smaller than 64 (wire: TextWidth)

        :param text_string: the text string is utf8 string and lenght is smaller than 512 (wire: TextString)

        :param speed: the scroll speed if it need scroll, the time (ms) the text move one step (wire: speed)

        :param color: the font color, eg:#FFFF00 (wire: color)

        :param align: horizontal text alignment, 0:scroll,2:normal; 3: middle aligned; 4:left aligned;5:right aligned, it will support at 90102 version (wire: align)

        Sources: https://docin.divoom-gz.com/web/#/5/134
        """
        return self.call("send_text", lcd_index=lcd_index, text_id=text_id, x=x, y=y, dir=dir, font=font, text_width=text_width, text_string=text_string, speed=speed, color=color, align=align)

    def clear_text(self, *, lcd_id: int, text_id: int) -> dict[str, Any]:
        """Clear text area.

        :param lcd_id: lcd index (wire: LcdId)

        :param text_id: it will clear all if it is samller than 0 (wire: TextId)

        Sources: https://docin.divoom-gz.com/web/#/5/141
        """
        return self.call("clear_text", lcd_id=lcd_id, text_id=text_id)

    def get_fonts(self) -> dict[str, Any]:
        """Get font list.

        Sources: https://docin.divoom-gz.com/web/#/5/131
        """
        return self.call("get_fonts")

    def send_display_list(self, *, lcd_index: int, new_flag: int, backgroud_gif: str, item_list: list[Any]) -> dict[str, Any]:
        """Send display list .

        :param lcd_index: the lcd id 0~4 (wire: LcdIndex)

        :param new_flag: 0:add display items，1： Overwrite the old display items and use new items (wire: NewFlag)

        :param backgroud_gif: the lcd backgroud image address, it only support gif file, it can't be updated, It will be ignored if NewFlag is 1 (wire: BackgroudGif)

        :param item_list: item list (wire: ItemList)

        Sources: https://docin.divoom-gz.com/web/#/5/132
        """
        return self.call("send_display_list", lcd_index=lcd_index, new_flag=new_flag, backgroud_gif=backgroud_gif, item_list=item_list)

    def send_command_list(self, *, command_list: list[Any]) -> dict[str, Any]:
        """Command list.

        :param command_list: the command array information (wire: CommandList)

        Sources: https://docin.divoom-gz.com/web/#/5/135
        """
        return self.call("send_command_list", command_list=command_list)

    def use_command_url(self, *, command_url: str) -> dict[str, Any]:
        """Url Command file.

        :param command_url: the url address of the command array information (wire: CommandUrl)

        Sources: https://docin.divoom-gz.com/web/#/5/136
        """
        return self.call("use_command_url", command_url=command_url)

class TimeFrame(BaseDevice):
    """TimeFrame operations from the official WiFi reference."""
    product_name = "timeframe"

    def reboot(self) -> dict[str, Any]:
        """System reboots.

        Sources: https://docin.divoom-gz.com/web/#/5/359
        """
        return self.call("reboot")

    def set_countdown(self, *, minute: int, second: int, status: int) -> dict[str, Any]:
        """Set countdown tool.

        :param minute: the countdown's minute (wire: Minute)

        :param second: the countdown's second (wire: Second)

        :param status: 1: start; 0: stop (wire: Status)

        Sources: https://docin.divoom-gz.com/web/#/5/370
        """
        return self.call("set_countdown", minute=minute, second=second, status=status)

    def set_stopwatch(self, *, status: int) -> dict[str, Any]:
        """Set stopwatch tool.

        :param status: 2:reset;1: start; 0: stop (wire: Status)

        Sources: https://docin.divoom-gz.com/web/#/5/371
        """
        return self.call("set_stopwatch", status=status)

    def set_scoreboard(self, *, blue_score: int, red_score: int) -> dict[str, Any]:
        """Set scoreboard tool.

        :param blue_score: the blue score 0~999 (wire: BlueScore)

        :param red_score: the red score 0~999 (wire: RedScore)

        Sources: https://docin.divoom-gz.com/web/#/5/372
        """
        return self.call("set_scoreboard", blue_score=blue_score, red_score=red_score)

    def set_noise_tool(self, *, noise_status: int) -> dict[str, Any]:
        """Set noise tool.

        :param noise_status: 1:start; 0:stop (wire: NoiseStatus)

        Sources: https://docin.divoom-gz.com/web/#/5/373
        """
        return self.call("set_noise_tool", noise_status=noise_status)

    def set_brightness(self, *, brightness: int) -> dict[str, Any]:
        """set brightness.

        :param brightness: 0~100 (wire: Brightness)

        Sources: https://docin.divoom-gz.com/web/#/5/362
        """
        return self.call("set_brightness", brightness=brightness)

    def set_weather_location(self, *, longitude: str, latitude: str) -> dict[str, Any]:
        """Weather area setting.

        :param longitude: value (wire: Longitude)

        :param latitude: value (wire: Latitude)

        Sources: https://docin.divoom-gz.com/web/#/5/363
        """
        return self.call("set_weather_location", longitude=longitude, latitude=latitude)

    def set_screen(self, *, on_off: int) -> dict[str, Any]:
        """Screen switch.

        :param on_off: 1:on; 0:off (wire: OnOff)

        Sources: https://docin.divoom-gz.com/web/#/5/367
        """
        return self.call("set_screen", on_off=on_off)

    def set_mirror_mode(self, *, mode: int) -> dict[str, Any]:
        """Set  Mirror mode.

        :param mode: 0:disable;1:enalbe (wire: Mode)

        Sources: https://docin.divoom-gz.com/web/#/5/368
        """
        return self.call("set_mirror_mode", mode=mode)

    def set_hour_mode(self, *, mode: int) -> dict[str, Any]:
        """Set  hour mode.

        :param mode: 1:24－hour;0:12-hour (wire: Mode)

        Sources: https://docin.divoom-gz.com/web/#/5/369
        """
        return self.call("set_hour_mode", mode=mode)

    def get_dial_list(self, *, device_id: int | None = None, start_num: int, end_num: int, device_type: str | None = None) -> dict[str, Any]:
        """Dial Type.

        :param device_id: device id (wire: DeviceId)

        :param start_num: >=1 (wire: StartNum)

        :param end_num: >=1 (wire: EndNum)

        :param device_type: Frame (wire: DeviceType)

        Sources: https://docin.divoom-gz.com/web/#/5/360
        """
        return self.call("get_dial_list", device_id=device_id, start_num=start_num, end_num=end_num, device_type=device_type)

    def select_clock(self, *, clock_id: int) -> dict[str, Any]:
        """Select faces Channel.

        :param clock_id: face id (wire: ClockId)

        Sources: https://docin.divoom-gz.com/web/#/5/361
        """
        return self.call("select_clock", clock_id=clock_id)

    def enter_custom_mode(self, *, backgroud_image_addr: str, backgroud_image_local_flag: int, disp_list: list[Any]) -> dict[str, Any]:
        """Enter custom display mode.

        :param backgroud_image_addr: Display base image, it will is url  and The resolution of the image must be 800 * 1280 (wire: BackgroudImageAddr)

        :param backgroud_image_local_flag: 1: "BackgroudImageAddr" will be a local file("/userdata/clock_bg.jpg");  0: it will be url file (wire: BackgroudImageLocalFlag)

        :param disp_list: list (wire: DispList)

        Sources: https://docin.divoom-gz.com/web/#/5/374
        """
        return self.call("enter_custom_mode", backgroud_image_addr=backgroud_image_addr, backgroud_image_local_flag=backgroud_image_local_flag, disp_list=disp_list)

    def exit_custom_mode(self) -> dict[str, Any]:
        """Exit custom display mode.

        Sources: https://docin.divoom-gz.com/web/#/5/375
        """
        return self.call("exit_custom_mode")

    def update_display_items(self, *, disp_list: list[Any]) -> dict[str, Any]:
        """Update Text Content.

        :param disp_list: list (wire: DispList)

        Sources: https://docin.divoom-gz.com/web/#/5/377
        """
        return self.call("update_display_items", disp_list=disp_list)

    def get_fonts(self, *, device_id: int | None = None) -> dict[str, Any]:
        """Get font list.

        :param device_id: Device ID. Omitted in page 379; live service requires a nonempty request. Automatically supplied from discovery (verified 2026-10-27). (wire: DeviceId)

        Sources: https://docin.divoom-gz.com/web/#/5/379
        """
        return self.call("get_fonts", device_id=device_id)

class AstroToo(BaseDevice):
    """AstroToo operations from the official WiFi reference."""
    product_name = "astrotoo"

    def get_hardware_version(self) -> dict[str, Any]:
        """Get hardware and firmware version.

        Sources: https://docin.divoom-gz.com/web/#/5/382
        """
        return self.call("get_hardware_version")

    def get_lan_capabilities(self) -> dict[str, Any]:
        """Get LAN capabilities.

        Sources: https://docin.divoom-gz.com/web/#/5/383
        """
        return self.call("get_lan_capabilities")

    def get_device_id(self) -> dict[str, Any]:
        """Get device ID.

        Sources: https://docin.divoom-gz.com/web/#/5/384
        """
        return self.call("get_device_id")

    def get_brightness(self) -> dict[str, Any]:
        """Get brightness.

        Sources: https://docin.divoom-gz.com/web/#/5/386
        """
        return self.call("get_brightness")

    def get_screen(self) -> dict[str, Any]:
        """Get screen state.

        Sources: https://docin.divoom-gz.com/web/#/5/387
        """
        return self.call("get_screen")

    def get_current_clock(self) -> dict[str, Any]:
        """Get current clock.

        Sources: https://docin.divoom-gz.com/web/#/5/388
        """
        return self.call("get_current_clock")

    def get_storage_status(self) -> dict[str, Any]:
        """Get storage status.

        Sources: https://docin.divoom-gz.com/web/#/5/389
        """
        return self.call("get_storage_status")

    def get_weather(self) -> dict[str, Any]:
        """Get cached weather.

        Sources: https://docin.divoom-gz.com/web/#/5/390
        """
        return self.call("get_weather")

    def get_screen_snapshot(self) -> dict[str, Any]:
        """Get screen snapshot.

        Sources: https://docin.divoom-gz.com/web/#/5/391
        """
        return self.call("get_screen_snapshot")

    def set_brightness(self, *, brightness: int) -> dict[str, Any]:
        """Set brightness.

        :param brightness: Required. 0 to 100; 0 is minimum brightness, not screen off. (wire: Brightness)

        Sources: https://docin.divoom-gz.com/web/#/5/392
        """
        return self.call("set_brightness", brightness=brightness)

    def set_screen(self, *, on_off: int) -> dict[str, Any]:
        """Screen switch.

        :param on_off: Required. 0: off; 1: on. (wire: OnOff)

        Sources: https://docin.divoom-gz.com/web/#/5/393
        """
        return self.call("set_screen", on_off=on_off)

    def set_hour_mode(self, *, mode: int) -> dict[str, Any]:
        """Set hour mode.

        :param mode: Required. 0: 12-hour format; 1: 24-hour format. (wire: Mode)

        Sources: https://docin.divoom-gz.com/web/#/5/398
        """
        return self.call("set_hour_mode", mode=mode)

    def set_temperature_mode(self, *, mode: int) -> dict[str, Any]:
        """Set temperature mode.

        :param mode: Required. 0: Celsius; 1: Fahrenheit. (wire: Mode)

        Sources: https://docin.divoom-gz.com/web/#/5/399
        """
        return self.call("set_temperature_mode", mode=mode)

    def get_local_albums(self) -> dict[str, Any]:
        """Get local album list.

        Sources: https://docin.divoom-gz.com/web/#/5/401
        """
        return self.call("get_local_albums")

    def get_local_photos(self, *, clock_id: int, start_num: int, end_num: int) -> dict[str, Any]:
        """Get local photo list.

        :param clock_id: Required. Local album ID, at least 100000. (wire: ClockId)

        :param start_num: Required. One-based first position, at least 1. (wire: StartNum)

        :param end_num: Required. Inclusive last position; StartNum <= EndNum <= StartNum + 99. (wire: EndNum)

        Sources: https://docin.divoom-gz.com/web/#/5/402
        """
        return self.call("get_local_photos", clock_id=clock_id, start_num=start_num, end_num=end_num)

    def set_album_cover(self, *, clock_id: int, photo_id: int) -> dict[str, Any]:
        """Set album cover.

        :param clock_id: Required. Existing normal local album ID. (wire: ClockId)

        :param photo_id: Required. Existing photo ID in that album. (wire: PhotoId)

        Sources: https://docin.divoom-gz.com/web/#/5/406
        """
        return self.call("set_album_cover", clock_id=clock_id, photo_id=photo_id)

    def add_photos_to_album(self, *, to_clock_id: int, photo_list: list[Any], parent_item_id: int | None = None, parent_clock_id: int | None = None) -> dict[str, Any]:
        """Add existing photos to album.

        :param to_clock_id: Required. Existing normal local album ID. (wire: ToClockId)

        :param photo_list: Required. Nonempty list of PhotoId values returned by Photo/GetPhotoList. (wire: PhotoList)

        :param parent_item_id: Use 0 for standalone local photo-library albums. (wire: ParentItemId)

        :param parent_clock_id: Use 0 for standalone local photo-library albums. (wire: ParentClockId)

        Sources: https://docin.divoom-gz.com/web/#/5/407
        """
        return self.call("add_photos_to_album", to_clock_id=to_clock_id, photo_list=photo_list, parent_item_id=parent_item_id, parent_clock_id=parent_clock_id)

    def remove_photos_from_album(self, *, clock_id: int, photo_list: list[Any], parent_item_id: int | None = None, parent_clock_id: int | None = None) -> dict[str, Any]:
        """Remove photos from album.

        :param clock_id: Required. Existing normal local album ID. (wire: ClockId)

        :param photo_list: Required. Nonempty list of PhotoId values returned by Photo/GetPhotoList. (wire: PhotoList)

        :param parent_item_id: Use 0 for standalone local photo-library albums. (wire: ParentItemId)

        :param parent_clock_id: Use 0 for standalone local photo-library albums. (wire: ParentClockId)

        Sources: https://docin.divoom-gz.com/web/#/5/408
        """
        return self.call("remove_photos_from_album", clock_id=clock_id, photo_list=photo_list, parent_item_id=parent_item_id, parent_clock_id=parent_clock_id)

    def delete_photos(self, *, clock_id: int, photo_list: list[Any], parent_item_id: int | None = None, parent_clock_id: int | None = None) -> dict[str, Any]:
        """Delete local photos.

        :param clock_id: Required. Existing normal local album ID. (wire: ClockId)

        :param photo_list: Required. Nonempty list of PhotoId values returned by Photo/GetPhotoList. (wire: PhotoList)

        :param parent_item_id: Use 0 for standalone local photo-library albums. (wire: ParentItemId)

        :param parent_clock_id: Use 0 for standalone local photo-library albums. (wire: ParentClockId)

        Sources: https://docin.divoom-gz.com/web/#/5/409
        """
        return self.call("delete_photos", clock_id=clock_id, photo_list=photo_list, parent_item_id=parent_item_id, parent_clock_id=parent_clock_id)

    def set_album_config(self, *, slideshow_theme: int, slideshow_speed: int, sub_slideshow_theme: int, fill_frame: int, frame_background: int, display_order: int, reverse_photo_order: int, show_title: int, show_clock: int, show_weather: int, video_auto_play: int, video_play_back: int, video_auto_mute: int, video_volume: int) -> dict[str, Any]:
        """Set album playback configuration.

        :param slideshow_theme: Required. Main slideshow effect ID. 0 selects the normal effect. (wire: SlideshowTheme)

        :param slideshow_speed: Required. Slideshow speed percentage, 0 to 100. Higher values shorten the dwell interval; this is neither milliseconds nor FPS. (wire: SlideshowSpeed)

        :param sub_slideshow_theme: Required. Effect ID for embedded slideshow views; 0 selects normal. (wire: SubSlideshowTheme)

        :param fill_frame: Required. 0: horizontal fill; 1: vertical fill, following the device setting. (wire: FillFrame)

        :param frame_background: Required. Device background-style ID; use an ID supported by the target device. (wire: FrameBackground)

        :param display_order: Required. 0: save time; 1: capture time; 2: random; 3: normal; 4: sticker layout. (wire: DisplayOrder)

        :param reverse_photo_order: Required. 0: newest first; 1: oldest first for time ordering. (wire: ReversePhotoOrder)

        :param show_title: Required. 0: hide title; 1: show title. (wire: ShowTitle)

        :param show_clock: Required. 0: hide clock overlay; 1: show clock overlay. (wire: ShowClock)

        :param show_weather: Required. 0: hide weather overlay; 1: show cached weather overlay. (wire: ShowWeather)

        :param video_auto_play: Required. 0: disable automatic video playback; 1: enable. (wire: VideoAutoPlay)

        :param video_play_back: Required. 0: loop; 1: play once; 2: play once and continue. (wire: VideoPlayBack)

        :param video_auto_mute: Required. 0: disable; 1: enable automatic mute after extended video playback. (wire: VideoAutoMute)

        :param video_volume: Required. Playback volume, 0 to 100. (wire: VideoVolume)

        Sources: https://docin.divoom-gz.com/web/#/5/412
        """
        return self.call("set_album_config", slideshow_theme=slideshow_theme, slideshow_speed=slideshow_speed, sub_slideshow_theme=sub_slideshow_theme, fill_frame=fill_frame, frame_background=frame_background, display_order=display_order, reverse_photo_order=reverse_photo_order, show_title=show_title, show_clock=show_clock, show_weather=show_weather, video_auto_play=video_auto_play, video_play_back=video_play_back, video_auto_mute=video_auto_mute, video_volume=video_volume)

    def upload_media(self, *, file_path: str | Path, clock_id: int, parent_item_id: int | None = None, parent_clock_id: int | None = None, user_id: int | None = None, photo_x: int | None = None, photo_y: int | None = None, photo_width: int | None = None, photo_height: int | None = None, photo_index: int | None = None, photo_total_cnt: int | None = None, photo_flag: int | None = None, send_time: float | None = None, taking_time: float | None = None, file_name: str | None = None, preview_file_name: str | None = None, photo_title: str | None = None, preview_path: str | Path | None = None, video_duration: float | None = None) -> dict[str, Any]:
        """Upload local photo or video.

        :param file_path: Local file path; streamed as the binary file part. (wire: file_path)

        :param clock_id: Required. Existing normal local album ID >= 100000. (wire: ClockId)

        :param parent_item_id: Required. Use 0 for standalone local albums. (wire: ParentItemId)

        :param parent_clock_id: Required. Use 0 for standalone local albums. (wire: ParentClockId)

        :param user_id: Required. Local owner metadata; use 0 when no application user is associated. (wire: UserId)

        :param photo_x: Required. Crop or positioning metadata; use 0 for an uncropped image. (wire: PhotoX)

        :param photo_y: Required. Crop or positioning metadata; use 0 for an uncropped image. (wire: PhotoY)

        :param photo_width: Required. Actual media dimensions in pixels. (wire: PhotoWidth)

        :param photo_height: Required. Actual media dimensions in pixels. (wire: PhotoHeight)

        :param photo_index: Required. Zero-based index in this transfer batch. (wire: PhotoIndex)

        :param photo_total_cnt: Required. Number of media items in the batch; 1 for one item. (wire: PhotoTotalCnt)

        :param photo_flag: Required. Batch marker; keep it consistent within a batch and use a different value for a new batch. (wire: PhotoFlag)

        :param send_time: Required. Saved time in Unix milliseconds; local database storage uses milliseconds. (wire: SendTime)

        :param taking_time: Required. Capture time in Unix milliseconds; firmware converts this field to seconds. (wire: TakingTime)

        :param file_name: Required. Bare media filename matching the multipart filename, below 128 UTF-8 bytes. (wire: FileName)

        :param preview_file_name: Required. Empty string for an image; bare uploaded preview filename for a video, below 128 UTF-8 bytes. (wire: PreviewFileName)

        :param photo_title: Required. UTF-8 title, below 512 bytes; an empty title is allowed. (wire: PhotoTitle)

        :param preview_path: Required WebP preview file for a video. (wire: preview_path)

        :param video_duration: Required declared video duration in seconds. (wire: video_duration)

        Sources: https://docin.divoom-gz.com/web/#/5/413
        """
        return self.call("upload_media", file_path=file_path, clock_id=clock_id, parent_item_id=parent_item_id, parent_clock_id=parent_clock_id, user_id=user_id, photo_x=photo_x, photo_y=photo_y, photo_width=photo_width, photo_height=photo_height, photo_index=photo_index, photo_total_cnt=photo_total_cnt, photo_flag=photo_flag, send_time=send_time, taking_time=taking_time, file_name=file_name, preview_file_name=preview_file_name, photo_title=photo_title, preview_path=preview_path, video_duration=video_duration)

    def download_media(self, *, path: str, destination: str | Path) -> Path:
        """Download local media.

        :param path: Exact device-returned /userdata/ path. (wire: path)

        :param destination: New local file path; existing files are never overwritten. (wire: destination)

        Sources: https://docin.divoom-gz.com/web/#/5/414
        """
        return self.call("download_media", path=path, destination=destination)

    def get_local_clock(self, *, clock_id: int | None = None, use_current_display_clock: int | None = None) -> dict[str, Any]:
        """Get local clock configuration.

        :param clock_id: Optional. Existing local clock ID. If omitted, use the current displayed clock. (wire: ClockId)

        :param use_current_display_clock: Optional. 1 selects the current displayed clock and takes precedence over ClockId. (wire: UseCurrentDisplayClock)

        Sources: https://docin.divoom-gz.com/web/#/5/415
        """
        return self.call("get_local_clock", clock_id=clock_id, use_current_display_clock=use_current_display_clock)

    def patch_local_clock(self, *, clock_id: int | None = None, use_current_display_clock: int | None = None, clock_name: str | None = None, item_patch_list: list[Any] | None = None) -> dict[str, Any]:
        """Patch local clock configuration.

        :param clock_id: Required unless UseCurrentDisplayClock is 1. Existing local clock ID. (wire: ClockId)

        :param use_current_display_clock: Optional. 1 targets the currently displayed clock. (wire: UseCurrentDisplayClock)

        :param clock_name: Optional. Rename the clock; 1 to 63 UTF-8 bytes. (wire: ClockName)

        :param item_patch_list: Optional. Entries contain zero-based index and patch object. At least one actual change is recommended. (wire: ItemPatchList)

        Sources: https://docin.divoom-gz.com/web/#/5/416
        """
        return self.call("patch_local_clock", clock_id=clock_id, use_current_display_clock=use_current_display_clock, clock_name=clock_name, item_patch_list=item_patch_list)

    def get_local_fonts(self) -> dict[str, Any]:
        """Get local font list.

        Sources: https://docin.divoom-gz.com/web/#/5/417
        """
        return self.call("get_local_fonts")

    def upload_clock_asset(self, *, file_path: str | Path) -> dict[str, Any]:
        """Upload local clock asset.

        :param file_path: Local file path; streamed as the binary file part. (wire: file_path)

        Sources: https://docin.divoom-gz.com/web/#/5/418
        """
        return self.call("upload_clock_asset", file_path=file_path)

    def create_local_clock(self, *, file_path: str | Path, clock_name: str, item_list: list[Any]) -> dict[str, Any]:
        """Create local clock.

        :param file_path: Local file path; streamed as the binary file part. (wire: file_path)

        :param clock_name: Required. Nonempty clock name; keep to at most 63 UTF-8 bytes. (wire: ClockName)

        :param item_list: Required. Nonempty array of display elements; see fields below. (wire: ItemList)

        Sources: https://docin.divoom-gz.com/web/#/5/419
        """
        return self.call("create_local_clock", file_path=file_path, clock_name=clock_name, item_list=item_list)

    def patch_clock_background(self, *, file_path: str | Path, clock_id: int | None = None, use_current_display_clock: int | None = None, clock_name: str | None = None, item_patch_list: list[Any] | None = None) -> dict[str, Any]:
        """Patch clock with background image.

        :param file_path: Local file path; streamed as the binary file part. (wire: file_path)

        :param clock_id: Required unless UseCurrentDisplayClock is 1. Existing local clock ID. (wire: ClockId)

        :param use_current_display_clock: Optional. 1 targets the currently displayed clock. (wire: UseCurrentDisplayClock)

        :param clock_name: Optional. Rename the clock; 1 to 63 UTF-8 bytes. (wire: ClockName)

        :param item_patch_list: Optional. Entries contain zero-based index and patch object. At least one actual change is recommended. (wire: ItemPatchList)

        Sources: https://docin.divoom-gz.com/web/#/5/420
        """
        return self.call("patch_clock_background", file_path=file_path, clock_id=clock_id, use_current_display_clock=use_current_display_clock, clock_name=clock_name, item_patch_list=item_patch_list)

    def replace_clock_background(self, *, file_path: str | Path, clock_id: int | None = None, use_current_display_clock: int | None = None) -> dict[str, Any]:
        """Replace clock background.

        :param file_path: Local file path; streamed as the binary file part. (wire: file_path)

        :param clock_id: Required unless UseCurrentDisplayClock is 1. Existing local clock ID. (wire: ClockId)

        :param use_current_display_clock: Optional. 1 targets the displayed clock. (wire: UseCurrentDisplayClock)

        Sources: https://docin.divoom-gz.com/web/#/5/421
        """
        return self.call("replace_clock_background", file_path=file_path, clock_id=clock_id, use_current_display_clock=use_current_display_clock)

    def get_countdown(self) -> dict[str, Any]:
        """Get countdown tool.

        Sources: https://docin.divoom-gz.com/web/#/5/422
        """
        return self.call("get_countdown")

    def set_countdown(self, *, minute: int, second: int, status: int) -> dict[str, Any]:
        """Set countdown tool.

        :param minute: Required. Nonnegative minute count. A conservative client range is 0 to 59. (wire: Minute)

        :param second: Required. 0 to 59. (wire: Second)

        :param status: Required. 1: start from supplied duration; 0: stop/pause. (wire: Status)

        Sources: https://docin.divoom-gz.com/web/#/5/423
        """
        return self.call("set_countdown", minute=minute, second=second, status=status)

    def get_stopwatch(self) -> dict[str, Any]:
        """Get stopwatch tool.

        Sources: https://docin.divoom-gz.com/web/#/5/424
        """
        return self.call("get_stopwatch")

    def set_stopwatch(self, *, status: int) -> dict[str, Any]:
        """Set stopwatch tool.

        :param status: Required. 1: start/resume; 0: pause; 2: reset. (wire: Status)

        Sources: https://docin.divoom-gz.com/web/#/5/425
        """
        return self.call("set_stopwatch", status=status)

    def get_scoreboard(self) -> dict[str, Any]:
        """Get scoreboard tool.

        Sources: https://docin.divoom-gz.com/web/#/5/426
        """
        return self.call("get_scoreboard")

    def set_scoreboard(self, *, blue_score: int, red_score: int) -> dict[str, Any]:
        """Set scoreboard tool.

        :param blue_score: Required. Nonnegative blue score; keep within the scoreboard UI range. (wire: BlueScore)

        :param red_score: Required. Nonnegative red score; keep within the scoreboard UI range. (wire: RedScore)

        Sources: https://docin.divoom-gz.com/web/#/5/427
        """
        return self.call("set_scoreboard", blue_score=blue_score, red_score=red_score)

    def get_noise_tool(self) -> dict[str, Any]:
        """Get noise tool.

        Sources: https://docin.divoom-gz.com/web/#/5/428
        """
        return self.call("get_noise_tool")

    def set_noise_tool(self, *, noise_status: int) -> dict[str, Any]:
        """Set noise tool.

        :param noise_status: Required. 0: off; 1: on. (wire: NoiseStatus)

        Sources: https://docin.divoom-gz.com/web/#/5/429
        """
        return self.call("set_noise_tool", noise_status=noise_status)

    def head_media(self, *, path: str) -> dict[str, str]:
        """Read headers of a device-returned /userdata/ path without downloading it."""
        return self.call("head_media", path=path)
