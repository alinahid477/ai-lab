// components/DownloadButton.tsx
import { useState } from 'react'
import { useAppContext } from "@/context/AppContext";
import { FileDown } from "lucide-react"
import {Button} from "@/components/ui/button"
interface DownloadButtonProps {
  /** The full path (on the server) to the file you want to download */
  filepath: string
  /** Optional: override the filename that the browser will save as */
  downloadFilename?: string
}

export default function DownloadButton({
  filepath,
  downloadFilename,
}: DownloadButtonProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string|null>(null)

  const { myAppContext} = useAppContext(); 

  const handleDownload = async () => {
    setLoading(true)
    setError(null)
    try {
      // 1. Call your FastAPI endpoint
      const res = await fetch(
        `${myAppContext.ENVVARS.AIBACKEND_SERVER}/downloadfile?filepath=${encodeURIComponent(filepath)}`,
        {
          method: 'GET',
          headers: {
            // if your endpoint requires auth, add your token here
            // 'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (!res.ok) {
        // handle 404, 500, etc.
        const detail = await res.text()
        throw new Error(`Server responded ${res.status}: ${detail}`)
      }

      // 2. Grab the response as a Blob
      const blob = await res.blob()

      // 3. Create an object URL and force a download
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url

      // if you want to override the name the user sees, use downloadFilename;
      // otherwise extract it from filepath:
      a.download =
        // downloadFilename ??
        filepath.split('/').pop() ??
        'downloaded-file.csv'

      document.body.appendChild(a)
      a.click()

      // 4. Cleanup
      a.remove()
      window.URL.revokeObjectURL(url)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      console.error(err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <Button
        variant="ghost"
        onClick={handleDownload}
        disabled={loading}
        className="h-8 px-2 lg:px-3"
      >
        {loading ? (
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-300"></div>
          </div>
        ) : (
          <><FileDown/> Download</>
        )}
      </Button>
      {/* {error && (
        <p style={{ color: 'red', marginTop: '0.5rem' }}>
          Error: {error}
        </p>
      )} */}
    </div>
  )
}