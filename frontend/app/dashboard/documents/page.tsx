"use client"

import { useState } from "react"
import { FileText, Loader2, Plus, Trash2, Upload } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export default function DocumentsPage() {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [documents, setDocuments] = useState([
    {
      id: "1",
      name: "Technical Manual v2.3.pdf",
      size: "4.2 MB",
      date: "2 days ago",
      status: "Processed",
    },
    {
      id: "2",
      name: "Field Guide 2025.pdf",
      size: "2.8 MB",
      date: "1 week ago",
      status: "Processed",
    },
    {
      id: "3",
      name: "Equipment Specs.pdf",
      size: "8.5 MB",
      date: "2 weeks ago",
      status: "Processed",
    },
  ])

  const handleUpload = () => {
    setIsUploading(true)
    setUploadProgress(0)

    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsUploading(false)
          // Add new document
          setDocuments([
            {
              id: `${documents.length + 1}`,
              name: "New Technical Document.pdf",
              size: "3.7 MB",
              date: "Just now",
              status: "Processing",
            },
            ...documents,
          ])
          return 0
        }
        return prev + 5
      })
    }, 200)
  }

  const handleDelete = (id: string) => {
    setDocuments(documents.filter((doc) => doc.id !== id))
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Documents</h2>
          <p className="text-muted-foreground">Upload and manage your technical documentation</p>
        </div>
        <Button onClick={handleUpload} disabled={isUploading}>
          {isUploading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="mr-2 h-4 w-4" />
              Upload Document
            </>
          )}
        </Button>
      </div>

      {isUploading && (
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium">Uploading document...</p>
                <p className="text-sm font-medium">{uploadProgress}%</p>
              </div>
              <Progress value={uploadProgress} />
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="all">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="all">All Documents</TabsTrigger>
            <TabsTrigger value="recent">Recently Added</TabsTrigger>
            <TabsTrigger value="processing">Processing</TabsTrigger>
          </TabsList>
          <div className="flex items-center gap-2">
            <p className="text-sm text-muted-foreground">{documents.length} documents</p>
          </div>
        </div>

        <TabsContent value="all" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>All Documents</CardTitle>
              <CardDescription>All your uploaded technical documentation</CardDescription>
            </CardHeader>
            <CardContent>
              {documents.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <FileText className="h-12 w-12 text-muted-foreground" />
                  <h3 className="mt-4 text-lg font-medium">No documents</h3>
                  <p className="mt-2 text-center text-sm text-muted-foreground">
                    You haven't uploaded any documents yet. Upload your first document to get started.
                  </p>
                  <Button onClick={handleUpload} className="mt-4">
                    <Plus className="mr-2 h-4 w-4" />
                    Upload Document
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {documents.map((doc) => (
                    <div key={doc.id} className="flex items-center justify-between rounded-lg border p-4">
                      <div className="flex items-center gap-4">
                        <FileText className="h-10 w-10 text-primary" />
                        <div>
                          <p className="font-medium">{doc.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {doc.size} • Uploaded {doc.date}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <span
                          className={`text-sm font-medium ${
                            doc.status === "Processed" ? "text-green-500" : "text-amber-500"
                          }`}
                        >
                          {doc.status}
                        </span>
                        <Button variant="ghost" size="icon" onClick={() => handleDelete(doc.id)}>
                          <Trash2 className="h-4 w-4 text-muted-foreground" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
            <CardFooter className="border-t bg-muted/50 px-6 py-3">
              <div className="flex items-center justify-between w-full text-xs text-muted-foreground">
                <p>Free plan: 3 of 3 documents used</p>
                <Button variant="link" size="sm" className="h-auto p-0">
                  Upgrade for unlimited documents
                </Button>
              </div>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="recent" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Recently Added</CardTitle>
              <CardDescription>Documents added in the last 7 days</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {documents
                  .filter((doc) => doc.date.includes("day") || doc.date.includes("Just now"))
                  .map((doc) => (
                    <div key={doc.id} className="flex items-center justify-between rounded-lg border p-4">
                      <div className="flex items-center gap-4">
                        <FileText className="h-10 w-10 text-primary" />
                        <div>
                          <p className="font-medium">{doc.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {doc.size} • Uploaded {doc.date}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <span
                          className={`text-sm font-medium ${
                            doc.status === "Processed" ? "text-green-500" : "text-amber-500"
                          }`}
                        >
                          {doc.status}
                        </span>
                        <Button variant="ghost" size="icon" onClick={() => handleDelete(doc.id)}>
                          <Trash2 className="h-4 w-4 text-muted-foreground" />
                        </Button>
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="processing" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Processing</CardTitle>
              <CardDescription>Documents currently being processed</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {documents.filter((doc) => doc.status === "Processing").length === 0 ? (
                  <Alert>
                    <AlertTitle>No documents processing</AlertTitle>
                    <AlertDescription>All your documents have been processed successfully.</AlertDescription>
                  </Alert>
                ) : (
                  documents
                    .filter((doc) => doc.status === "Processing")
                    .map((doc) => (
                      <div key={doc.id} className="flex items-center justify-between rounded-lg border p-4">
                        <div className="flex items-center gap-4">
                          <FileText className="h-10 w-10 text-primary" />
                          <div>
                            <p className="font-medium">{doc.name}</p>
                            <p className="text-sm text-muted-foreground">
                              {doc.size} • Uploaded {doc.date}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-sm font-medium text-amber-500">{doc.status}</span>
                          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                        </div>
                      </div>
                    ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Card>
        <CardHeader>
          <CardTitle>Document Upload Guidelines</CardTitle>
          <CardDescription>Follow these guidelines for optimal results</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <h3 className="font-medium">Supported Formats</h3>
                <ul className="list-disc pl-5 text-sm text-muted-foreground">
                  <li>PDF documents (.pdf)</li>
                  <li>Word documents (.docx, .doc)</li>
                  <li>Text files (.txt)</li>
                  <li>Markdown files (.md)</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h3 className="font-medium">Size Limits</h3>
                <ul className="list-disc pl-5 text-sm text-muted-foreground">
                  <li>Maximum file size: 50MB</li>
                  <li>Maximum pages: 500</li>
                  <li>Free plan: 3 documents total</li>
                  <li>Pro plan: Unlimited documents</li>
                </ul>
              </div>
            </div>
            <div className="space-y-2">
              <h3 className="font-medium">Best Practices</h3>
              <ul className="list-disc pl-5 text-sm text-muted-foreground">
                <li>Use searchable PDFs for best results</li>
                <li>Ensure documents are not password protected</li>
                <li>For complex diagrams, include descriptive text</li>
                <li>Processing typically takes 1-5 minutes per document</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

