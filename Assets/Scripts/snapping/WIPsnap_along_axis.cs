using UnityEngine;

[ExecuteAlways]
public class snap_along_axis : MonoBehaviour
{
    public enum Axis {X,Y,Z}
    public Axis snapAxis = Axis.X;
    public Transform snapTarget;



    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if(snapTarget != null)
        {
            Vector3 targetPos = snapTarget.position;
            Vector3 curPos = GetComponent<Transform>().position;

            switch (snapAxis)
            {
                case Axis.X:
                    targetPos.z = curPos.z;
                    targetPos.y = curPos.y;
                    break;
                case Axis.Y:
                    targetPos.z = curPos.z;
                    targetPos.x = curPos.x;
                    break;
                case Axis.Z:
                    targetPos.x = curPos.x;
                    targetPos.y = curPos.y;
                    break;
            }

            snapTarget.transform.position = targetPos;
        }
    }
}
