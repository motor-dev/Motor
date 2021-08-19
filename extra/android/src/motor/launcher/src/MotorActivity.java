package com.motor;

import android.app.Activity;
import android.content.pm.PackageManager;
import android.content.pm.ActivityInfo;
import android.os.Bundle;
import android.util.Log;
import android.view.WindowManager;

import java.io.File;


public class MotorActivity extends Activity
{
    MotorView mView;

    @Override protected void onCreate(Bundle icicle)
    {
        super.onCreate(icicle);
        String plugin = "";
        try
        {
            ActivityInfo ai = getPackageManager().getActivityInfo(this.getComponentName(), PackageManager.GET_META_DATA);
            Bundle metaData = ai.metaData;
            plugin = metaData.getString("app", "");
        }
        catch(PackageManager.NameNotFoundException e)
        {
        }
        String apkPath = getApplicationInfo().sourceDir;
        String dataPath = getApplicationInfo().dataDir;
        Log.i("Motor", "Running motor app " + plugin);
        MotorLib.setPaths(apkPath, dataPath, plugin);
        mView = new MotorView(getApplication());
        setContentView(mView);
    }

    @Override protected void onPause()
    {
        super.onPause();
        mView.onPause();
    }

    @Override protected void onResume()
    {
        super.onResume();
        mView.onResume();
    }
}
