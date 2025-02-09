from phpcomment.utils.patcher_v3 import PatcherV3, PatchError

patcher = PatcherV3()

original = """\
def hello():
    print("Hello World")

def goodbye():
    print("Goodbye World")
"""

diff = """\
--- a/file.py
+++ b/file.py
@@ -1,5 +1,5 @@
 def hello():
-    print("Hello World")
+    print("Hello, Universe!")

 def goodbye():
     print("Goodbye World")
"""

def main():

    try:
        modified = patcher.apply_patch(original, diff)
        print(modified)
    except PatchError as e:
        print(f"Error applying patch: {e}")


if __name__ == "__main__":
    main()