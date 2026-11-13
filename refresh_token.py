"""يطبع رمزًا جديدًا (صالحًا 60 يومًا) فقط على stdout — يستعمله workflow تجديد الرمز."""
import os, publish
print(publish.refresh_token(os.environ["IG_ACCESS_TOKEN"]), end="")
