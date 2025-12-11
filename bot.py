# در تابع finish_photos این بخش رو اصلاح کن

# پایان ثبت عکس‌ها و ارسال نهایی
@dp.message(MotorForm.photos, Command("finish"))
async def finish_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    
    if not photos:
        await message.answer("⚠️ حداقل یک عکس الزامی است!\nلطفاً حداقل یک عکس از موتور ارسال کنید.")
        return
    
    # ساخت متن نهایی آگهی - بدون Markdown مشکلساز
    ad_text = (
        "🏍 آگهی فروش 🏍\n\n"
        f"🏍 مدل: {data['model']}\n"
        f"📅 سال ساخت: {data['year']}\n"
        f"🎨 رنگ: {data['color']}\n"
        f"🛣 کارکرد: {data['mileage']} کیلومتر\n"
        f"📍 محل: {data['location']}\n"
        f"📞 تماس: {data['contact']}\n\n"
        f"👤 ثبت کننده: {message.from_user.full_name}\n"
        f"🆔 @{message.from_user.username or 'بدون یوزرنیم'}"
    )
    
    # پاکسازی متن از کاراکترهای مشکل‌ساز
    def clean_text(text):
        # حذف کاراکترهای نامتعارف
        problematic_chars = ['<', '>', '&', '`']
        for char in problematic_chars:
            text = text.replace(char, '')
        # حذف Markdown ناقص
        text = text.replace('*', '').replace('_', '').replace('`', '')
        # محدود کردن طول
        if len(text) > 1000:
            text = text[:1000] + "..."
        return text
    
    cleaned_text = clean_text(ad_text)
    
    # ارسال به مالک (مدیر)
    if OWNER_CHAT_ID:
        try:
            # همیشه از media group استفاده می‌کنیم
            media_group = []
            
            # همه عکس‌ها را به آلبوم اضافه می‌کنیم
            for i, photo_id in enumerate(photos):
                if i == 0:  # عکس اول با کپشن
                    media_group.append(
                        InputMediaPhoto(
                            media=photo_id,
                            caption=cleaned_text,  # متن پاکسازی‌شده
                            parse_mode="HTML"  # تغییر از Markdown به HTML
                        )
                    )
                else:  # عکس‌های بعدی بدون کپشن
                    media_group.append(
                        InputMediaPhoto(media=photo_id)
                    )
            
            # ارسال آلبوم
            await bot.send_media_group(
                chat_id=OWNER_CHAT_ID,
                media=media_group
            )
            
            await message.answer("✅ آگهی شما با موفقیت ثبت و برای مدیر ارسال شد.\nبرای ثبت آگهی جدید روی /start کلیک کنید.")
            logger.info(f"✅ آگهی موتور برای مالک (ID: {OWNER_CHAT_ID}) ارسال شد. {len(photos)} عکس.")
            
        except Exception as e:
            error_msg = f"❌ خطا در ارسال آگهی: {e}"
            await message.answer(error_msg)
            logger.error(f"❌ خطا در ارسال آگهی به مالک: {e}")
            
            # لاگ متن مشکل‌ساز
            logger.error(f"🔍 متن مشکل‌ساز: {ad_text[:200]}")
    else:
        await message.answer("⚠️ تنظیمات مدیر یافت نشد.")
    
    await state.clear()
